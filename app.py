import gradio as gr
import cv2
import base64
from openai import OpenAI

# JSONデータの例
apartment_json = '''{
  "apartment": {
    "name": "My Apartment",
    "rectangle": {
        "x": 0,
        "y": 0,
        "width": 9.0,
        "height": 7.0
    },
    "rooms": [
      {
        "name": "Living Room",
        "rectangle": {
          "x": 0,
          "y": 0,
          "width": 5.0,
          "height": 4.0
        },
        "features": [
          {
            "type": "window",
            "rectangle": {
              "x": 2,
              "y": 0,
              "width": 1.0,
              "height": 0.125
            }
          },
          {
            "type": "door",
            "rectangle": {
              "x": 5,
              "y": 3,
              "width": 0.125,
              "height": 1.0
            }
          },
          {
            "type": "door",
            "rectangle": {
              "x": 2,
              "y": 4,
              "width": 1.0,
              "height": 0.125
            }
          },
          {
            "type": "door",
            "rectangle": {
              "x": 4,
              "y": 4,
              "width": 1.0,
              "height": 0.125
            }
          }
        ]
      },
      {
        "name": "Bedroom",
        "rectangle": {
          "x": 5.0,
          "y": 0,
          "width": 4.0,
          "height": 4.0
        },
        "features": [
          {
            "type": "window",
            "rectangle": {
              "x": 7.0,
              "y": 0,
              "width": 1.0,
              "height": 0.125
            }
          }
        ]
      },
      {
        "name": "Kitchen",
        "rectangle": {
          "x": 0,
          "y": 4.0,
          "width": 3.0,
          "height": 3.0
        },
        "features": []
      },
      {
        "name": "Bathroom",
        "rectangle": {
          "x": 3.0,
          "y": 4.0,
          "width": 2.0,
          "height": 3.0
        },
        "features": []
      }
    ]
  }
}'''


def process_video(video_path, seconds_per_frame=2):
    base64Frames = []
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()

    return base64Frames


def summarize_video(api_key, file_path):
    client = OpenAI(api_key=api_key)

    # フレームと音声を抽出 (秒間0.5フレーム)
    base64Frames = process_video(file_path, seconds_per_frame=0.25)
    print(f"len(base64Frames): {len(base64Frames)}")

    # GPT-4oで要約生成
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """あなたは優秀な建築士です。提供された動画から図面を書き起こしてください

図面は以下のように処理されます:

```
# JSONをPythonの辞書に変換
apartment_data = json.loads(apartment_json)

# 図面の描画
fig, ax = plt.subplots()
for room in apartment_data["apartment"]["rooms"]:
    room_rect = room["rectangle"]
    ax.add_patch(patches.Rectangle((room_rect["x"], room_rect["y"]), room_rect["width"], room_rect["height"], edgecolor='black', facecolor='none'))
    plt.text(room_rect["x"] + room_rect["width"]/2, room_rect["y"] + room_rect["height"]/2, room["name"],
             horizontalalignment='center', verticalalignment='center')

    for feature in room["features"]:
        feature_rect = feature["rectangle"]
        if feature["type"] == "window":
            color = 'blue'
        elif feature["type"] == "door":
            color = 'green'
        else:
            color = 'red'
        ax.add_patch(patches.Rectangle((feature_rect["x"], feature_rect["y"]), feature_rect["width"], feature_rect["height"], edgecolor=color, facecolor='none'))

ax.set_xlim(0, apartment_data["apartment"]["rectangle"]["width"])
ax.set_ylim(0, apartment_data["apartment"]["rectangle"]["height"])
ax.set_aspect('equal')
plt.gca().invert_yaxis()
plt.show()
```

apartment_jsonのサンプルは以下の通りです:
{apartment_json}

""",
            },
            {
                "role": "user",
                "content": [
                    "これらは動画から取得されたフレームです",
                    *map(
                        lambda x: {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpg;base64,{x}",
                                "detail": "low",
                            },
                        },
                        base64Frames,
                    ),
                    {
                        "type": "text",
                        "text": f"""あなたは優秀な建築士です。提供された動画から指示に従いjson形式で図面を作成してください。""",
                    },
                ],
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content

demo = gr.Interface(
    fn=summarize_video,
    inputs=[gr.Textbox(label="OpenAI API Key"), gr.File(label="Upload Video (mp4)")],
    outputs="markdown",
    title="Madori Generator",
    description="動画をアップロードしOpenAIのAPIキーを入力すると部屋のレイアウトのjsonが生成されます。API使用料にご注意ください。",
)

if __name__ == "__main__":
    demo.launch()