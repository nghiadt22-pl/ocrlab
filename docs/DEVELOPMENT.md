# Development Guidelines

## Code Organization

### Frontend Structure
```
src/
├── components/    # Reusable UI components
├── lib/          # Shared utilities and API clients
├── pages/        # Page components and routing
└── styles/       # Global styles and themes
```

### Backend Structure
```
function_app/
├── function_app.py   # Main Azure Functions code
├── requirements.txt  # Python dependencies
└── host.json        # Azure Functions configuration
```

## Development Workflow

### Local Development
1. Start the frontend:
   ```bash
   npm run dev
   ```

2. Start the Azure Function:
   ```bash
   cd function_app
   func start
   ```

### Making Changes
1. Create a new branch for your feature
2. Make changes and test locally
3. Update documentation if needed
4. Deploy to staging for testing
5. Deploy to production

## Testing

### Frontend Testing
- Use React Testing Library for component tests
- Test user interactions and UI states
- Run tests with `npm test`

### Backend Testing
- Test Azure Functions locally first
- Use Postman or similar for API testing
- Test with different file types and sizes

## Deployment

### Frontend Deployment
1. Build the production version:
   ```bash
   npm run build:prod
   ```

2. Test the build locally:
   ```bash
   npm run preview
   ```

### Backend Deployment
1. Deploy Azure Functions:
   ```bash
   npm run deploy:function
   ```

## Common Tasks

### Adding a New API Endpoint
1. Create new function in `function_app.py`
2. Add CORS options handler
3. Update frontend API client
4. Test locally before deployment

### Updating Dependencies
1. Frontend:
   ```bash
   npm update
   ```

2. Backend:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

## Troubleshooting

### CORS Issues
1. Check allowed origins in `host.json`
2. Verify CORS headers in responses
3. Test with browser developer tools

### Azure Function Issues
1. Check function logs
2. Verify environment variables
3. Test endpoints locally

### File Upload Issues
1. Check file size limits
2. Verify blob storage permissions
3. Check network request in browser

## Best Practices

### Code Style
- Use TypeScript for frontend code
- Follow Python PEP 8 for backend code
- Write meaningful comments
- Keep functions small and focused

### Security
- Never commit sensitive data
- Use environment variables for credentials
- Validate user input
- Handle errors gracefully

### Performance
- Optimize file uploads
- Use proper caching
- Implement pagination
- Monitor API response times

## Documentation
- Keep this documentation updated
- Document API changes
- Update PROGRESS.md for major changes
- Document known issues and workarounds 