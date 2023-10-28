# Form Automation Project

This project aims to automate the submission of forms for reporting impersonation issues on Twitter.

## Environment Setup

### Dependencies

The project's dependencies are specified in the `requirements.txt` file. To install them, run the following command:

```bash
pip install -r requirements.txt
```

### Environment Variables

This project uses environment variables for configuration. You should create an `.env` file based on the provided `.env.template` file.

1. Copy `.env.template` and rename it to `.env`.
2. Open `.env` and fill in the variables with appropriate values.

## Running the Project

To run the project, follow these steps:

1. Make sure all dependencies are installed.
2. Complete the environment variables setup.

```bash
python src/main.py
```

## Testing the selenium

If for some reason you don't want to test with the database, you can easily run selenium without. Just uncomment:

```python
 if __name__ == "__main__":
     complete_impersonation_form('https://help.twitter.com/en/forms/authenticity/impersonation', 'profile_id', 'company_name', 'path_to_a_pdf')
```

In the `form_handler.py` file and then

```bash
python src/form_handler.py
```
