variable "region" {
  description = "Home region of the free-plan account (India accounts are pinned to Sydney)."
  type        = string
  default     = "ap-southeast-2"
}

variable "bedrock_regions" {
  description = "Regions tried in order for Bedrock inference. New accounts are unlocked region by region; the Lambda remembers the first that answers."
  type        = list(string)
  default     = ["us-west-2", "eu-west-2", "us-east-1", "us-east-2", "eu-central-1", "ap-northeast-1", "ap-southeast-1", "ap-southeast-2"]
}

variable "bedrock_vision_model" {
  description = "Multimodal model used to read the bill image."
  type        = string
  default     = "amazon.nova-lite-v1:0"
}

variable "bedrock_text_model" {
  description = "Text model used to write the proposal. Anthropic needs the one-time use-case form; Nova Pro is the automatic fallback."
  type        = string
  default     = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
}

variable "bedrock_fallback_models" {
  description = "Tried in order when the primary model is denied or throttled."
  type        = list(string)
  default     = ["amazon.nova-pro-v1:0", "amazon.nova-lite-v1:0"]
}
