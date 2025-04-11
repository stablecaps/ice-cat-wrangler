#!/usr/bin/env python3.12

import argparse
import os
import random
import sys

from helpers.cat_api_client import CatAPIClient
from helpers.config import (
    load_environment_variables,
)
from rich import print


class CLIArgs:
    """Setup arparse CLI options using dispatch pattern."""

    def __init__(self):
        help_banner = (
            "./client_launcher.py --secretsfile dev_conf_secrets --debug analyse --imgpath /path/to/image.jpg\n"
            "./client_launcher.py --secretsfile dev_conf_secrets --debug results --resultid 120\n"
            "./client_launcher.py --secretsfile ssm --debug analyse --imgpath /path/to/image.jpg\n"
        )

        parser = argparse.ArgumentParser(
            description="ICE Cat API Client",
            usage=".e.g: ./client_launcher.py {--secretsfile [ssm|dev_conf_secrets]} [--debug] {bulkanalyse|result|bulkresults} [<args>]\n"
            + help_banner,
        )
        # Global args
        parser.add_argument(
            "--secretsfile",
            "-s",
            type=str,
            required=True,
            help="Secrets file name located in config folder to load environment variables from, or 'ssm' to fetch from AWS SSM Parameter Store.",
        )
        parser.add_argument(
            "--debug",
            "-d",
            action="store_true",
            required=False,
            default=False,
            help="Debug mode. Set to True to enable debug output.",
        )

        # Subparsers for commands
        subparsers = parser.add_subparsers(dest="command", required=True)

        ########################################
        # Subparser for "bulk_analyse"
        bulk_analyse_parser = subparsers.add_parser(
            "bulkanalyse",
            help="Bulk upload images from local directory to AWS S3 bucket",
        )
        bulk_analyse_parser.add_argument(
            "--folder",
            "-f",
            type=str,
            required=True,
            default="./bulk_images",
            help="Path to the local folder containing images to upload.",
        )

        ########################################
        # Subparser for "results"
        result_parser = subparsers.add_parser(
            "result", help="Get results from AWS Lambda results function"
        )
        result_parser.add_argument(
            "--batchid",
            "-b",
            dest="batch_id",
            type=str,
            required=True,
            help="Batch ID to get results for. e.g. 1234567890",
        )
        result_parser.add_argument(
            "--imgfprint",
            "-p",
            dest="img_fprint",
            type=str,
            required=True,
            help="Image fingerprint hash to get results for. e.g. a91c54f1f00...",
        )

        #######################################
        # Subparser for "bulkresults"
        bulkresult_parser = subparsers.add_parser(
            "bulkresults", help="Upload local image to AWS Lambda analyse function"
        )
        # bulkresults.add_argument(
        #     "--imgpath",
        #     "-i",
        #     dest="img_path",
        #     type=str,
        #     required=True,
        #     help="Path to the local image to upload. e.g. /path/to/image.jpg",
        # )

        ########################################
        args = parser.parse_args()

        if not hasattr(CLIArgs, args.command):
            print("Unrecognized command")
            parser.print_help()
            sys.exit(42)

        # Load environment variables
        load_environment_variables(secretsfile=args.secretsfile, debug=args.debug)

        print("All environment secrets set correctly")

        # Get the client ID
        client_id = CLIArgs.get_client_id()

        # Dispatch to the appropriate subcommand
        if args.command == "bulkanalyse":
            CLIArgs.bulkanalyse(args.folder, client_id, args.debug)
        elif args.command == "result":
            CLIArgs.result(args.batch_id, args.img_fprint, args.debug)
        elif args.command == "bulkresults":
            CLIArgs.bulkresults(args.result_id, args.debug)

    @staticmethod
    def get_client_id():
        """
        Searches for a file named 'client_id' in the 'config' folder.
        If found, reads and returns the client ID from the file.

        Returns:
            str: The client ID read from the file.

        Raises:
            SystemExit: If the file is not found or is empty.
        """
        config_folder = os.path.join(os.getcwd(), "config")
        client_id_file = os.path.join(config_folder, "client_id")

        if not os.path.isfile(client_id_file):
            print(
                f"\nError: 'client_id' file not found in the 'config' folder: {config_folder}"
            )
            print("Dev helper automatically creating file")

            client_id = f"stablecaps{random.randint(100, 999)}"
            with open(client_id_file, "w") as file:
                file.write(client_id)
            print(f"'client_id' file created with ID: {client_id}")

        else:
            with open(client_id_file, "r") as file:
                client_id = file.read().strip()

        if not client_id:
            print(f"Error: 'client_id' not found. Exiting...")
            sys.exit(42)

        print(f"Client ID loaded successfully: {client_id}\n")
        return client_id

    @staticmethod
    def bulkanalyse(folder, client_id, debug):

        CatAPIClient(
            action="bulkanalyse", folder_path=folder, client_id=client_id, debug=debug
        )

    @staticmethod
    def result(batch_id, img_fprint, debug):

        client = CatAPIClient(
            action="result", batch_id=batch_id, img_fprint=img_fprint, debug=debug
        )

    @staticmethod
    def bulkresults(debug):
        print("Bulk results not implemented yet. Exiting...")
        return


if __name__ == "__main__":

    CLIArgs()

    print("\nFinished")
