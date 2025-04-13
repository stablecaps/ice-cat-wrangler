#!/usr/bin/env python3.12

import argparse
import os
import random
import sys

from helpers.cat_api_client import CatAPIClient
from helpers.config import (
    load_environment_variables,
)
from helpers.general import read_file_2string, write_batch_file, write_string_2file
from rich import print


class CLIArgs:
    """
    Handles command-line interface (CLI) arguments and dispatches commands
    to the appropriate subcommand handlers.

    This class sets up argparse to parse CLI arguments, validates them,
    and executes the corresponding functionality based on the provided
    subcommand.
    """

    def __init__(self):
        """
        Initializes the CLI argument parser, defines global arguments,
        subcommands, and their respective arguments. Dispatches the
        appropriate subcommand based on user input.
        """

        help_banner = (
            "./client_launcher.py --secretsfile ssm --debug bulkanalyse --folder_path bulk_uploads/\n"
            "./client_launcher.py --secretsfile ssm result --imgfprint f54c84046c5ad95fa2f0f686db515bada71951cb0dde2ed37f76708a173033f7 --batchid 1744370618\n"
            "./client_launcher.py --secretsfile ssm bulkresults --batchfile logs/stablecaps900_batch-1744377772.json\n"
        )

        ########################################
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
            help="Secrets file name located in config folder_path to load environment variables from, or 'ssm' to fetch from AWS SSM Parameter Store.",
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
            dest="folder_path",
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
        bulkresult_parser.add_argument(
            "--batchfile",
            "-b",
            dest="batch_file",
            type=str,
            required=True,
            help="Path to the local batch logfile. Found in api-client/logs folder e.g.: logs/stablecaps900_batch-1744499247.json",
        )

        ########################################
        args = parser.parse_args()
        print("args:", args)

        if args.command not in ["bulkanalyse", "result", "bulkresults"]:
            print()
            parser.print_help()
            sys.exit(42)

        self.debug = args.debug

        # Load environment variables
        load_environment_variables(secretsfile=args.secretsfile, debug=self.debug)

        print("All environment secrets set correctly")

        # Get the client ID
        self.client_id = CLIArgs.get_client_id()

        CatAPIClient(
            action=args.command,
            client_id=self.client_id,
            # debug=args.debug,
            **vars(args),
        )

    @staticmethod
    def get_client_id():
        """
        Searches for a file named 'client_id' in the 'config' folder.
        If found, reads and returns the client ID from the file. If the file
        does not exist, it creates one with a randomly generated client ID.

        Returns:
            str: The client ID read from the file.

        Raises:
            SystemExit: If the file is empty or the client ID cannot be loaded.
        """
        config_folder = os.path.join(os.getcwd(), "config")
        client_id_file = os.path.join(config_folder, "client_id")

        if not os.path.isfile(client_id_file):
            print(
                f"\nError: 'client_id' file not found in the 'config' folder: {config_folder}"
            )
            print("Dev helper automatically creating file")

            client_id = f"stablecaps{random.randint(100, 999)}"
            write_string_2file(filepath=client_id_file, filetext=client_id, mode="w")
            print(f"'client_id' file created with ID: {client_id}")

        else:
            client_id = read_file_2string(filepath=client_id_file, mode="r")

        if not client_id:
            print(f"Error: 'client_id' not found. Exiting...")
            sys.exit(42)

        print(f"Client ID loaded successfully: {client_id}\n")
        return client_id

    # def bulkanalyse(self, folder_path):
    #     """
    #     Handles the 'bulkanalyse' subcommand. Uploads images from a local
    #     directory to an AWS S3 bucket.

    #     Args:
    #         folder_path (str): Path to the local folder_path containing images.
    #         client_id (str): The client ID for authentication.
    #         debug (bool): Debug mode flag.
    #     """
    #     CatAPIClient(
    #         action="bulkanalyse",
    #         folder_path=folder_path,
    #         client_id=self.client_id,
    #         debug=self.debug,
    #     )

    # def result(self, batch_id, img_fprint):
    #     """
    #     Handles the 'result' subcommand. Fetches results from dynamodb
    #     for a specific batch ID and image fingerprint.

    #     Args:
    #         batch_id (str): The batch ID to fetch results for.
    #         img_fprint (str): The image fingerprint hash.
    #         debug (bool): Debug mode flag.
    #     """
    #     client = CatAPIClient(
    #         action="result",
    #         batch_id=batch_id,
    #         img_fprint=img_fprint,
    #         client_id=self.client_id,
    #         debug=self.debug,
    #     )

    # def bulkresults(self, batch_file):
    #     """
    #     Handles the 'bulkresults' subcommand. Processes a batch file (created by bulkanalyse)
    #     to upload images and fetch results.

    #     Args:
    #         batch_file (str): Path to the local batch logfile.
    #         debug (bool): Debug mode flag.
    #     """
    #     client = CatAPIClient(
    #         action="bulkresults",
    #         batch_file=batch_file,
    #         client_id=self.client_id,
    #         debug=self.debug,
    #     )


if __name__ == "__main__":

    CLIArgs()

    print("\nFinished")
