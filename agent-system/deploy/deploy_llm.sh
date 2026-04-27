#!/bin/bash
vllm serve /workspace/yans2@xiaopeng.com/code/swift-xp/scripts/train/RL_result/moe-colocate-full-30B-instruct-with_AP_description_format_v2_from_2400_iter/v0-20260411-143918/checkpoint-300
  --port 8901 \
  --host 127.0.0.1 \
  --dtype bfloat16 \
  --max-model-len 65536 \
  --allowed-local-media-path /workspace/fengyx4@xiaopeng.com/fyx/hym/huangym/omni/dataset/output_20260317204133 \
  -tp 2