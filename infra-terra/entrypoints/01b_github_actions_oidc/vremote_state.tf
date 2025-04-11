### Get remote state
# https://stackoverflow.com/questions/61647617/use-terraform-state-output-from-another-project
data "terraform_remote_state" "ice_tf_remote_backend" {
  backend = "s3"
  config = {
    region = "eu-west-1"
    bucket = "terraform-remotestate-${var.company}-ice1-${var.env}"
    key    = "terraform-remotestate-${var.company}-${var.env}/terraform.tfstate"
  }
}
