import csv
import io
import json
import os
from datetime import datetime

import boto3


def lambda_handler(event, context):
    """
    Lambda function to generate compliance reports for PCI DSS, GDPR, and SOC 2
    """

    # Initialize AWS clients
    config_client = boto3.client("config")
    s3_client = boto3.client("s3")
    sns_client = boto3.client("sns")

    # Environment variables
    app_name = os.environ["APP_NAME"]
    environment = os.environ["ENVIRONMENT"]
    bucket_name = os.environ["BUCKET_NAME"]
    sns_topic = os.environ["SNS_TOPIC"]

    try:
        # Generate compliance report
        report_data = generate_compliance_report(config_client, app_name, environment)

        # Create CSV report
        csv_content = create_csv_report(report_data)

        # Upload to S3
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_key = (
            f"compliance-reports/{environment}/{timestamp}_compliance_report.csv"
        )

        s3_client.put_object(
            Bucket=bucket_name,
            Key=report_key,
            Body=csv_content,
            ContentType="text/csv",
            ServerSideEncryption="aws:kms",
        )

        # Generate summary report
        summary = generate_summary_report(report_data)

        # Send notification
        send_notification(sns_client, sns_topic, summary, report_key)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Compliance report generated successfully",
                    "report_location": f"s3://{bucket_name}/{report_key}",
                    "summary": summary,
                }
            ),
        }

    except Exception as e:
        print(f"Error generating compliance report: {str(e)}")

        # Send error notification
        error_message = f"Failed to generate compliance report: {str(e)}"
        sns_client.publish(
            TopicArn=sns_topic,
            Subject=f"Compliance Report Generation Failed - {app_name} {environment}",
            Message=error_message,
        )

        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


def generate_compliance_report(config_client, app_name, environment):
    """
    Generate comprehensive compliance report data
    """
    report_data = {"pci_dss": [], "gdpr": [], "soc2": [], "general": []}

    # Get all config rules
    config_rules = config_client.describe_config_rules()

    for rule in config_rules["ConfigRules"]:
        rule_name = rule["ConfigRuleName"]

        # Get compliance details for this rule
        try:
            compliance_details = config_client.get_compliance_details_by_config_rule(
                ConfigRuleName=rule_name
            )

            for result in compliance_details["EvaluationResults"]:
                compliance_data = {
                    "rule_name": rule_name,
                    "resource_type": result["EvaluationResultIdentifier"][
                        "EvaluationResultQualifier"
                    ]["ResourceType"],
                    "resource_id": result["EvaluationResultIdentifier"][
                        "EvaluationResultQualifier"
                    ]["ResourceId"],
                    "compliance_type": result["ComplianceType"],
                    "result_recorded_time": result["ResultRecordedTime"].isoformat(),
                    "annotation": result.get("Annotation", ""),
                    "config_rule_invoked_time": result[
                        "ConfigRuleInvokedTime"
                    ].isoformat(),
                }

                # Categorize by compliance framework
                if "pci" in rule_name.lower():
                    report_data["pci_dss"].append(compliance_data)
                elif "gdpr" in rule_name.lower():
                    report_data["gdpr"].append(compliance_data)
                elif "soc2" in rule_name.lower():
                    report_data["soc2"].append(compliance_data)
                else:
                    report_data["general"].append(compliance_data)

        except Exception as e:
            print(f"Error getting compliance details for rule {rule_name}: {str(e)}")
            continue

    return report_data


def create_csv_report(report_data):
    """
    Create CSV format compliance report
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "Framework",
            "Rule Name",
            "Resource Type",
            "Resource ID",
            "Compliance Status",
            "Last Evaluated",
            "Rule Invoked Time",
            "Annotation",
        ]
    )

    # Write data for each framework
    for framework, data in report_data.items():
        for item in data:
            writer.writerow(
                [
                    framework.upper(),
                    item["rule_name"],
                    item["resource_type"],
                    item["resource_id"],
                    item["compliance_type"],
                    item["result_recorded_time"],
                    item["config_rule_invoked_time"],
                    item["annotation"],
                ]
            )

    return output.getvalue()


def generate_summary_report(report_data):
    """
    Generate summary statistics for compliance report
    """
    summary = {
        "total_resources_evaluated": 0,
        "compliant_resources": 0,
        "non_compliant_resources": 0,
        "frameworks": {},
    }

    for framework, data in report_data.items():
        framework_summary = {
            "total": len(data),
            "compliant": 0,
            "non_compliant": 0,
            "compliance_percentage": 0,
        }

        for item in data:
            if item["compliance_type"] == "COMPLIANT":
                framework_summary["compliant"] += 1
                summary["compliant_resources"] += 1
            elif item["compliance_type"] == "NON_COMPLIANT":
                framework_summary["non_compliant"] += 1
                summary["non_compliant_resources"] += 1

        if framework_summary["total"] > 0:
            framework_summary["compliance_percentage"] = round(
                (framework_summary["compliant"] / framework_summary["total"]) * 100, 2
            )

        summary["frameworks"][framework] = framework_summary
        summary["total_resources_evaluated"] += framework_summary["total"]

    # Calculate overall compliance percentage
    if summary["total_resources_evaluated"] > 0:
        summary["overall_compliance_percentage"] = round(
            (summary["compliant_resources"] / summary["total_resources_evaluated"])
            * 100,
            2,
        )
    else:
        summary["overall_compliance_percentage"] = 0

    return summary


def send_notification(sns_client, sns_topic, summary, report_key):
    """
    Send notification with compliance report summary
    """
    message = f"""
Compliance Report Generated Successfully

Overall Compliance: {summary['overall_compliance_percentage']}%
Total Resources Evaluated: {summary['total_resources_evaluated']}
Compliant Resources: {summary['compliant_resources']}
Non-Compliant Resources: {summary['non_compliant_resources']}

Framework Breakdown:
"""

    for framework, data in summary["frameworks"].items():
        message += f"""
{framework.upper()}:
  - Total: {data['total']}
  - Compliant: {data['compliant']}
  - Non-Compliant: {data['non_compliant']}
  - Compliance Rate: {data['compliance_percentage']}%
"""

    message += f"""
Report Location: s3://{report_key}

Generated at: {datetime.now().isoformat()}
"""

    sns_client.publish(
        TopicArn=sns_topic,
        Subject=f"Compliance Report - {summary['overall_compliance_percentage']}% Overall Compliance",
        Message=message,
    )
