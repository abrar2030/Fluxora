# Contributing to Fluxora

Thank you for your interest in contributing to Fluxora! This guide will help you understand our development process and how to contribute effectively.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## Development Process

1. **Fork and Clone**
   - Fork the repository
   - Clone your fork
   - Set up the development environment (see [Setup Guide](setup.md))

2. **Branch Naming**
   - Feature branches: `feature/description`
   - Bug fixes: `fix/description`
   - Documentation: `docs/description`
   - Performance: `perf/description`
   - Refactoring: `refactor/description`

3. **Development Workflow**
   - Create a new branch
   - Make your changes
   - Write tests
   - Update documentation
   - Commit your changes
   - Push to your fork
   - Create a pull request

## Code Style

### Python (Backend)

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions and classes
- Maximum line length: 88 characters
- Use Black for formatting
- Use isort for import sorting

Example:
```python
from typing import List, Optional

def calculate_energy_usage(
    readings: List[float],
    time_period: Optional[int] = None
) -> float:
    """
    Calculate total energy usage from readings.

    Args:
        readings: List of energy readings
        time_period: Optional time period in hours

    Returns:
        Total energy usage
    """
    return sum(readings)
```

### JavaScript/TypeScript (Frontend)

- Use ESLint and Prettier
- Follow Airbnb style guide
- Use TypeScript for type safety
- Write JSDoc comments
- Maximum line length: 80 characters

Example:
```typescript
interface EnergyData {
  consumption: number;
  production: number;
  timestamp: string;
}

/**
 * Calculates net energy from consumption and production
 * @param data - Energy data object
 * @returns Net energy value
 */
const calculateNetEnergy = (data: EnergyData): number => {
  return data.consumption - data.production;
};
```

## Testing

### Backend Tests

- Write unit tests for all new code
- Use pytest for testing
- Maintain test coverage above 80%
- Include integration tests for API endpoints

Example:
```python
def test_calculate_energy_usage():
    readings = [100.0, 120.0, 110.0]
    result = calculate_energy_usage(readings)
    assert result == 330.0
```

### Frontend Tests

- Write unit tests for components
- Use Jest and React Testing Library
- Include integration tests for user flows
- Test error handling and edge cases

Example:
```typescript
describe('EnergyChart', () => {
  it('renders correctly with data', () => {
    const data = {
      consumption: [100, 120, 110],
      production: [80, 90, 85],
      timestamps: ['2024-01-01', '2024-01-02', '2024-01-03']
    };
    
    render(<EnergyChart data={data} />);
    expect(screen.getByTestId('energy-chart')).toBeInTheDocument();
  });
});
```

## Documentation

### Code Documentation

- Document all public APIs
- Include usage examples
- Keep documentation up to date
- Use clear and concise language

### Pull Request Documentation

- Clear title and description
- Link to related issues
- List changes made
- Include testing instructions
- Add screenshots for UI changes

## Review Process

1. **Code Review**
   - All PRs require at least one review
   - Address review comments
   - Keep PRs focused and small
   - Update PR as needed

2. **CI/CD Checks**
   - All tests must pass
   - Code style checks must pass
   - Documentation must be updated
   - No merge conflicts

3. **Final Review**
   - Maintainer review
   - Final approval
   - Merge to main branch

## Release Process

1. **Versioning**
   - Follow semantic versioning
   - Update version numbers
   - Update changelog
   - Tag releases

2. **Deployment**
   - Run deployment scripts
   - Verify deployment
   - Monitor for issues
   - Announce release

## Getting Help

- Check existing documentation
- Search closed issues
- Ask in Slack channel
- Create new issue if needed

## Additional Resources

- [Project Structure](../architecture/project-structure.md)
- [API Documentation](../api/README.md)
- [Testing Guide](testing.md)
- [Release Process](release-process.md) 