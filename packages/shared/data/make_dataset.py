# packages/shared/data/make_dataset.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from packages.shared.utils.logger import get_logger
# from packages.shared.data.feature_store import FeatureStoreClient # If integrating with feature store

logger = get_logger(__name__)

class DatasetMaker:
    """
    Handles the creation and preparation of datasets for model training and evaluation.
    This includes loading raw data, cleaning, splitting, and potentially saving processed datasets.
    """

    def __init__(self, raw_data_path: str, processed_data_dir: str = None, 
                 test_size: float = 0.2, validation_size: float = 0.1, random_state: int = 42):
        """
        Initializes the DatasetMaker.
        Args:
            raw_data_path (str): Path to the raw input data file (e.g., CSV, Parquet).
            processed_data_dir (str, optional): Directory to save processed datasets. 
                                                If None, processed data is not saved by default.
            test_size (float): Proportion of the dataset to include in the test split.
            validation_size (float): Proportion of the *remaining* dataset (after test split) 
                                     to include in the validation split. If 0, no validation set is created.
            random_state (int): Seed for random number generation for reproducibility.
        """
        self.raw_data_path = raw_data_path
        self.processed_data_dir = processed_data_dir
        self.test_size = test_size
        self.validation_size = validation_size
        self.random_state = random_state

        if self.processed_data_dir and not os.path.exists(self.processed_data_dir):
            os.makedirs(self.processed_data_dir, exist_ok=True)
            logger.info(f"Created directory for processed data: {self.processed_data_dir}")

    def load_raw_data(self) -> pd.DataFrame | None:
        """
        Loads raw data from the specified path.
        Supports CSV and Parquet files based on extension.
        Returns:
            pd.DataFrame: Loaded data as a Pandas DataFrame, or None if loading fails.
        """
        logger.info(f"Loading raw data from: {self.raw_data_path}")
        try:
            if not os.path.exists(self.raw_data_path):
                logger.error(f"Raw data file not found: {self.raw_data_path}")
                return None
            
            if self.raw_data_path.endswith(".csv"):
                df = pd.read_csv(self.raw_data_path)
            elif self.raw_data_path.endswith( (".parquet", ".pq")):
                df = pd.read_parquet(self.raw_data_path)
            else:
                logger.error(f"Unsupported file format: {self.raw_data_path}. Please use CSV or Parquet.")
                return None
            logger.info(f"Raw data loaded successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading raw data: {e}")
            return None

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs basic preprocessing steps on the DataFrame.
        This is a placeholder and should be customized for the specific dataset.
        Args:
            df (pd.DataFrame): The input DataFrame.
        Returns:
            pd.DataFrame: The preprocessed DataFrame.
        """
        logger.info("Starting data preprocessing...")
        # Example preprocessing steps:
        # 1. Handle missing values (e.g., fill with mean/median or drop)
        # df.fillna(df.mean(), inplace=True) # Example: fill with mean for numeric columns
        # df.dropna(inplace=True) # Example: drop rows with any NA

        # 2. Convert data types if necessary
        # for col in df.select_dtypes(include=["object"]).columns:
        #     try:
        #         df[col] = pd.to_numeric(df[col])
        #     except ValueError:
        #         logger.warning(f"Could not convert column {col} to numeric.")

        # 3. Feature engineering (can be done here or in a separate feature engineering step)
        # Example: df["new_feature"] = df["existing_col1"] / df["existing_col2"]

        logger.info(f"Data preprocessing completed. Shape after preprocessing: {df.shape}")
        return df

    def split_data(self, df: pd.DataFrame, target_column: str) -> tuple:
        """
        Splits the data into training, validation (optional), and test sets.
        Args:
            df (pd.DataFrame): The DataFrame to split.
            target_column (str): The name of the target variable column.
        Returns:
            tuple: (X_train, y_train, X_val, y_val, X_test, y_test) or (X_train, y_train, X_test, y_test)
                   Returns None for validation sets if validation_size is 0.
        """
        logger.info("Splitting data into training, validation, and test sets...")
        if target_column not in df.columns:
            logger.error(f"Target column 	{target_column}	 not found in DataFrame.")
            raise ValueError(f"Target column 	{target_column}	 not found.")

        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Split into training + (validation) and test sets
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y if y.nunique() > 1 and len(y) >= 2*y.nunique() else None
        )
        logger.info(f"Test set created. X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

        X_train, y_train = X_train_val, y_train_val
        X_val, y_val = None, None

        if self.validation_size > 0 and len(X_train_val) > 1:
            # Calculate actual validation proportion relative to the X_train_val set
            val_prop = self.validation_size / (1 - self.test_size)
            if val_prop < 1.0 : # Ensure val_prop is less than 1 to avoid splitting everything into validation
                try:
                    X_train, X_val, y_train, y_val = train_test_split(
                        X_train_val, y_train_val, test_size=val_prop, random_state=self.random_state, stratify=y_train_val if y_train_val.nunique() > 1 and len(y_train_val) >= 2*y_train_val.nunique() else None
                    )
                    logger.info(f"Training and validation sets created. X_train shape: {X_train.shape}, X_val shape: {X_val.shape}")
                except ValueError as e:
                    logger.warning(f"Could not stratify validation split, proceeding without stratification: {e}")
                    X_train, X_val, y_train, y_val = train_test_split(
                        X_train_val, y_train_val, test_size=val_prop, random_state=self.random_state
                    )
                    logger.info(f"Training and validation sets created (unstratified). X_train shape: {X_train.shape}, X_val shape: {X_val.shape}")
            else:
                logger.warning("Validation size too large for the remaining data after test split. Skipping validation set.")
                # X_train, y_train already set
        else:
            logger.info(f"Training set created (no validation set). X_train shape: {X_train.shape}")

        return X_train, y_train, X_val, y_val, X_test, y_test

    def save_processed_data(self, data_dict: dict):
        """
        Saves the processed datasets to the specified directory.
        Args:
            data_dict (dict): A dictionary where keys are dataset names (e.g., 	X_train	, 	y_test	)
                              and values are the Pandas DataFrames/Series to save.
        """
        if not self.processed_data_dir:
            logger.info("No processed_data_dir specified. Skipping saving processed data.")
            return

        for name, data in data_dict.items():
            if data is not None:
                try:
                    file_path = os.path.join(self.processed_data_dir, f"{name}.parquet")
                    if isinstance(data, pd.Series):
                        data.to_frame().to_parquet(file_path, index=False)
                    else:
                        data.to_parquet(file_path, index=False)
                    logger.info(f"Saved {name} to {file_path}")
                except Exception as e:
                    logger.error(f"Error saving {name} to {file_path}: {e}")

    def run(self, target_column: str) -> dict:
        """
        Executes the full dataset creation pipeline: load, preprocess, split, and save.
        Args:
            target_column (str): The name of the target variable column.
        Returns:
            dict: A dictionary containing the split datasets (X_train, y_train, etc.).
        """
        raw_df = self.load_raw_data()
        if raw_df is None:
            logger.error("Dataset creation failed: Could not load raw data.")
            return {}

        processed_df = self.preprocess_data(raw_df.copy()) # Use copy to avoid modifying original df
        
        X_train, y_train, X_val, y_val, X_test, y_test = self.split_data(processed_df, target_column)

        datasets = {
            "X_train": X_train, "y_train": y_train,
            "X_val": X_val, "y_val": y_val,
            "X_test": X_test, "y_test": y_test
        }

        self.save_processed_data(datasets)
        
        logger.info("Dataset creation pipeline completed.")
        return datasets

# Example Usage (assumes a CSV file named 	raw_data.csv	 in a 	data/raw	 directory)
if __name__ == "__main__":
    # Create dummy raw data for example
    if not os.path.exists("data/raw"):
        os.makedirs("data/raw")
    if not os.path.exists("data/processed"):
        os.makedirs("data/processed")

    dummy_data = pd.DataFrame({
        "feature1": range(100),
        "feature2": [x * 2 for x in range(100)],
        "feature3": [x % 3 for x in range(100)], # Categorical-like for stratification test
        "target": [x % 2 for x in range(100)]
    })
    dummy_data_path = "data/raw/sample_raw_data.csv"
    dummy_data.to_csv(dummy_data_path, index=False)
    logger.info(f"Created dummy raw data at {dummy_data_path}")

    dataset_maker = DatasetMaker(
        raw_data_path=dummy_data_path,
        processed_data_dir="data/processed",
        validation_size=0.1 # Create a validation set
    )
    
    # Specify the target column in your dataset
    created_datasets = dataset_maker.run(target_column="target")
    
    if created_datasets:
        logger.info("Accessing created datasets:")
        if created_datasets.get("X_train") is not None:
            logger.info(f"X_train shape: {created_datasets['X_train'].shape}")
        if created_datasets.get("X_val") is not None:
            logger.info(f"X_val shape: {created_datasets['X_val'].shape}")
        if created_datasets.get("X_test") is not None:
            logger.info(f"X_test shape: {created_datasets['X_test'].shape}")
    else:
        logger.error("No datasets were created.")

    # Clean up dummy data (optional - uncomment to remove created files/dirs)
    # if os.path.exists(dummy_data_path):
    #     os.remove(dummy_data_path)
    #     logger.info(f"Cleaned up dummy raw data: {dummy_data_path}")
    # if os.path.exists("data/processed") and os.path.isdir("data/processed"):
    #     for f_name in os.listdir("data/processed"):
    #         f_path = os.path.join("data/processed", f_name)
    #         if os.path.isfile(f_path):
    #             os.remove(f_path)
    #     if not os.listdir("data/processed"): # Only remove if empty
    #         os.rmdir("data/processed")
    # if os.path.exists("data/raw") and os.path.isdir("data/raw") and not os.listdir("data/raw"):
    #     os.rmdir("data/raw")
    # if os.path.exists("data") and os.path.isdir("data") and not os.listdir("data"):
    #     os.rmdir("data")
    #     logger.info("Cleaned up dummy processed data and directories if they were empty.")

