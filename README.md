## 概要

部屋の間取りを生成するアプリ (未完成)

## 課題

- GPT-4oの性能的に難しい
- 間取りは普通のアプローチで生成しようね: [RoomPlan](https://developer.apple.com/jp/augmented-reality/roomplan/) 等

## 使い方

### 事前準備

```
pip install -r requirements.txt
```

### Gradioの立ち上げ

```
python app.py
```

上記アプリに動画とOpenAI API Keyを貼り付け、jsonを生成する。
生成したjsonは適当なpathに保存する。

### 間取りの確認

```
python viewer.py <jsonのpath>
```

## 処理内容

- 部屋を動画として撮影
- 1秒4フレームで画像を抽出
- GPT-4oに画像群を渡し、jsonを生成
- jsonをviewerに渡し、描画

## 部屋の表現について

部屋の表現をjsonで表現している

1. apartment
    - rectangle: アパート全体のサイズを示すオブジェクト
        - width: アパートの幅
        - height: アパートの高さ
    - rooms: 部屋のリスト。各部屋は以下のフィールドを持つオブジェクト
2. rooms
    - name: 部屋の名前
        - rectangle: 部屋の位置とサイズを示すオブジェクト
            - x: 部屋の左上隅のX座標
            - y: 部屋の左上隅のY座標
            - width: 部屋の幅
            - height: 部屋の高さ
        - features: 部屋内の特徴的な設備のリスト。各設備は以下のフィールドを持つオブジェクト
3. features
    - type: 設備の種類（例：ドア、シンク、ストーブ、冷蔵庫など）
    - rectangle: 設備の位置とサイズを示すオブジェクト
        - x: 設備の左上隅のX座標
        - y: 設備の左上隅のY座標
        - width: 設備の幅
        - height: 設備の高さ