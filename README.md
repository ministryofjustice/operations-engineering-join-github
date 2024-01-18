# Operations Engineering Join GitHub

1. [Prerequisites](#prerequisites)
1. [Development](#development)
1. [Deployment](#deployment)

## Prerequisites

To develop, deploy or run this app, you will need to install the following:

- [Python 3.11](https://www.python.org/downloads/release/python-3110/)
- [Docker](https://www.docker.com/)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/)

## Development

### Environment setup

Set up the necessary environment variables. Refer to the .env.example file for the required format and variables. Create a .env file in the project root with the necessary configurations:

```bash
cp .env.example .env
# Edit .env to add the required configurations
source .env
```

### Run application within Terminal

Run the application locally from the terminal.

```bash
make local
```

Open a browser to http://127.0.0.1:4567

### Linting

To run the linter, run the following command:

```bash
make lint
```

Our project employs MegaLinter in our GitHub Actions to automatically ensure code quality on every pull request. It performs extensive linting across various languages and file formats, including Python, Bash, Markdown, Dockerfiles, JSON, Kubernetes configurations, and YAML. Configured in the .github/workflows/ directory, MegaLinter helps identify issues early, enforcing best practices and style guidelines.

### Testing

To run the tests, run the following command:

```bash
make test
```

## Deployment

### Tokens and Secrets

All necessary tokens and secrets required for the deployment processes are manually set in the GitHub repository secrets. These include access tokens for various services and sensitive configuration data.

### Deployment Pipelines

This project utilises two separate deployment pipelines:

#### Development Deployment Pipeline

To deploy to the `operations-engineering-join-github-dev` namespace, use the following steps:

1. Ensure your changes are committed to the `main` branch through the relevant pull request process.
2. The pipeline will automatically deploy the latest commit SHA to the development namespace using the Helm chart located in `helm/join-github`.

#### Production Deployment Pipeline

To deploy the latest tag push to GitHub in the production environment, follow these steps:

1. Clone the repository and ensure you have the latest updates from the `main` branch.
2. Create a new tag using the Git tagging system. For example, to create tag v0.0.1, run:

   ```bash
   git tag v0.0.1
   ```

> When creating a new tag, use semantic versioning (e.g., `v1.0.0`, `v1.0.1`). This practice helps in maintaining version control and understanding the nature of the changes (major, minor, or patch).

3. Push the tag to the repository:

    ```bash
    git push --tags
    ```

4. The pipeline will automatically deploy the application to the `operations-engineering-join-github-prod` namespace.

### Development environment

The Cloud Platform namespace for this project is called `operations-engineering-join-github-dev`.

You can see the development app running at: https://join-github-dev.cloud-platform.service.justice.gov.uk/

And access Cloud Platform's namespace using:

```bash
kubectl get pods -n operations-engineering-join-github-dev
```

### Production environment

The Cloud Platform namespace for the production environment is `operations-engineering-join-github-prod`.

You can see the production app running at: https://join-github.cloud-platform.service.justice.gov.uk/

To interact with the production environment, use kubectl commands. For example:

```bash
kubectl get pods -n operations-engineering-join-github-prod
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you want to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact Us

If you have any questions or need further clarification, feel free to ask in the #ask-operations-engineering channel on
Slack or email us at operations-engineering@digital.justice.gov.uk.
