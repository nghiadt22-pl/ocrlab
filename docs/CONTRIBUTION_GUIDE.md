
# Contribution Guide

This document provides guidelines for contributing to the Document Intelligence application.

## Getting Started

### Setting Up Your Development Environment

1. Fork the repository
2. Clone your fork to your local machine
3. Install dependencies:
```
npm install
```
4. Create a new branch for your feature or fix:
```
git checkout -b feature/your-feature-name
```

## Development Workflow

### Coding Standards

- Use TypeScript for all new code
- Follow the existing coding style (indentation, naming conventions, etc.)
- Add appropriate comments for complex logic
- Update type definitions when adding or modifying functionality

### Component Development

- Create focused, reusable components
- Use shadcn/ui components where appropriate
- Implement responsive design for all components
- Write tests for new components

### Submitting Changes

1. Commit your changes with clear, descriptive commit messages
2. Push your branch to your fork
3. Submit a pull request to the main repository
4. Address any feedback from code review

## Testing

### Running Tests

```
npm test
```

### Test Coverage

Aim for high test coverage, especially for:
- Azure service integrations
- File processing logic
- Error handling

## Documentation

### Code Documentation

- Add JSDoc comments to functions and components
- Keep documentation up-to-date when making changes

### Update README and Docs

When adding significant features or making important changes:
- Update the README.md file
- Update relevant documentation in the `/docs` directory
- Add examples for new functionality

## Versioning

We follow [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward-compatible manner
- PATCH version for backward-compatible bug fixes

## Troubleshooting Common Issues

### Azure Integration Issues

- Check Azure service status
- Verify API keys and endpoint configurations
- Check network connectivity and CORS configuration
- Review console logs for detailed error messages

### Build Problems

- Run `npm clean-install` to refresh dependencies
- Check for TypeScript errors with `npm run typecheck`
- Verify that all required environment variables are set

## Getting Help

- Check existing issues on GitHub
- Join our development chat on Discord
- Email the development team at dev@example.com
