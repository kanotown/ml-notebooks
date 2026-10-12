# Python機械学習スタートブック ノートブック

『Python機械学習スタートブック』の各章のコードと演習問題を Google Colab で実行するためのノートブック集です。

- Web教材: https://ml.kano.ac
- 各ノートブックは書籍の「リスト番号」順に本文コードを収録し、章末に演習問題（テンプレートコード付き）を収録しています
- 演習の解答例は [Web教材の解答ページ](https://ml.kano.ac/solutions/2/) に掲載しています

| 章 | ノートブック |
|---|---|
| 1. イントロダクション | [chapter01.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter01.ipynb) |
| 2. Python入門 | [chapter02.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter02.ipynb) |
| 3. データ可視化 | [chapter03.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter03.ipynb) |
| 4. 機械学習の基礎 | [chapter04.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter04.ipynb) |
| 5. 前処理と特徴量選択 | [chapter05.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter05.ipynb) |
| 6. 回帰 | [chapter06.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter06.ipynb) |
| 7. 分類 | [chapter07.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter07.ipynb) |
| 8. 木構造とアンサンブル学習 | [chapter08.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter08.ipynb) |
| 9. 教師なし学習 | [chapter09.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter09.ipynb) |
| 10. 画像処理の基礎 | [chapter10.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter10.ipynb) |
| 11. 画像データを用いた機械学習 | [chapter11.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter11.ipynb) |
| 12. 自然言語処理の基礎 | [chapter12.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter12.ipynb) |
| 13. テキストデータを用いた機械学習 | [chapter13.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter13.ipynb) |
| 14. 深層学習の基礎と活用 | [chapter14.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter14.ipynb) |
| 15. 機械学習アプリの作り方 | [chapter15.ipynb](https://colab.research.google.com/github/kanotown/ml-notebooks/blob/main/chapter15.ipynb) |

本文コード・演習は、校正を反映した `ml-web` を基準に同期します。最新版のTeX原稿が手元にないため、旧TeXからの再生成は行いません。

隣のディレクトリに `ml-web` を置き、このリポジトリで次を実行してください。

```powershell
python scripts/sync_from_web.py          # 第1〜14章を同期
python scripts/sync_from_web.py 5 6 13  # 指定章だけ同期
python scripts/sync_from_web.py --check  # 差分確認のみ（不一致なら終了コード1）
```

- 本文コード・入力キャプション：`ml-web/docs/code/N.md`
- 演習問題・テンプレート：`ml-web/docs/chapters/N.md`
- 解答例：`ml-web/includes/solutions/N-*.md`（ノートブックからリンク）

入力番号を保ったまま同期し、既存の節見出し・セルID・メタデータを維持します。変更したコードセルの出力は消去します。第15章の付録は別途手作業で保守します。

Colab で上から実行できるよう、各ノートブックのタイトルの直後に「準備」セル（日本語フォントの matplotlib-fontja、第13章は MeCab など）を、第11・13章は「演習問題」の直後に演習用データのダウンロードセルを置きます。どちらも `scripts/sync_from_web.py` の `SETUP`・`EXERCISE_DATA` で章ごとに設定しています。

旧原稿側の `generate_web_code.py` / `generate_notebooks.py` を実行すると、校正後のWebコード・ノートブックを上書きするため使用しないでください。
