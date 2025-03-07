# Azure Functions GitHub Actions Deployment

This directory contains GitHub Actions workflows for deploying the Azure Functions app.

## Available Workflows

1. **azure-functions-deploy.yml** - Uses the Azure Functions GitHub Action
2. **azure-functions-cli-deploy.yml** - Uses the Azure Functions Core Tools CLI directly

You can choose which workflow to use based on your preferences.

## Setup Instructions

To set up the GitHub Actions deployment, you need to configure the following secrets in your GitHub repository:

### 1. AZURE_CREDENTIALS

This secret contains the Azure service principal credentials for GitHub Actions to authenticate with Azure.

To create this secret:

1. Install the Azure CLI and login:
   ```
   az login
   ```

2. Create a service principal:
   ```
   az ad sp create-for-rbac --name "github-actions-testpl" --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} --sdk-auth
   ```
   Replace `{subscription-id}` and `{resource-group}` with your Azure subscription ID and resource group name.

3. Copy the entire JSON output and add it as a secret named `AZURE_CREDENTIALS` in your GitHub repository.

### 2. AZURE_FUNCTIONAPP_PUBLISH_PROFILE

This secret contains the publish profile for your Azure Function App.

To get the publish profile:

1. Go to the Azure Portal and navigate to your Function App (testpl).
2. Click on "Get publish profile" and download the file.
3. Open the downloaded file and copy its entire contents.
4. Add the contents as a secret named `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` in your GitHub repository.

**Note:** The publish profile is only required for the `azure-functions-deploy.yml` workflow. The CLI-based workflow uses Azure CLI authentication instead.

## Workflow Comparison

### Azure Functions GitHub Action (azure-functions-deploy.yml)

- Uses the official Azure Functions GitHub Action
- Requires the AZURE_FUNCTIONAPP_PUBLISH_PROFILE secret
- Handles build and deployment in a more integrated way
- May provide better error handling and logging

### Azure Functions CLI (azure-functions-cli-deploy.yml)

- Uses the Azure Functions Core Tools CLI directly
- More similar to the command you would run locally (`func azure functionapp publish testpl`)
- Requires installing the Azure Functions Core Tools via npm
- May provide more flexibility for custom deployment scenarios

## Workflow Configuration

The workflow is configured to:

- Trigger on pushes to the `main` branch that modify files in the `function_app` directory
- Allow manual triggering via the GitHub Actions UI
- Set up Python 3.10
- Install dependencies from `requirements.txt`
- Deploy the function app to Azure

## Customization

You can customize either workflow by modifying the respective YAML file:

- Change the trigger branches or paths
- Modify the Python version
- Add additional build or test steps
- Configure environment variables

## Troubleshooting

If the deployment fails, check the GitHub Actions logs for error messages. Common issues include:

- Incorrect secrets configuration
- Missing dependencies
- Azure resource access permissions
- Function app configuration issues 