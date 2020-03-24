import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from jinja2 import Environment, PackageLoader, select_autoescape
import argparse
from slugify import slugify

def stripRelative(path) -> str:
	return path.replace("../../../", "", 1)

def processSheet(output_path) -> None:
	env = Environment(
		loader=PackageLoader('gsheet2md', 'templates'),
		autoescape=select_autoescape(['html', 'xml'])
	)
	# use creds to create a client to interact with the Google Drive API
	scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes)
	client = gspread.authorize(creds)
	# Find a workbook by name and open the first sheet
	# Make sure you use the right name here.
	sheet = client.open("Collaboration tools").sheet1
	# Extract and print all of the values
	tools = sheet.get_all_records()
	tool_page_template = env.get_template('tool.md.jinja2')
	generated_page_paths = [None] * len(tools)
	for tool in tools:
		name_slug = tool['Slug']
		page_path = f"{output_path}/{name_slug}.md"
		tool_page_template.stream(tool=tool).dump(page_path)
		index = int(tool['Sequence']) - 1
		generated_page_paths[index] = stripRelative(page_path)


	registry_data = {"pages": generated_page_paths}
	registry_file_basename = 'collaboration-tools.json'
	registry_template = env.get_template(f"{registry_file_basename}.jinja2")
	registry_template.stream(registry_contents=registry_data).dump(f"{output_path}/{registry_file_basename}")


def init_argparse() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		usage="%(prog)s [OUTPUT_PATH]...",
		description="Generate a collection of markdown files."
	)
	parser.add_argument('OUTPUT_PATH')
	return parser


parser = init_argparse()
args = parser.parse_args()
processSheet(output_path=args.OUTPUT_PATH)
