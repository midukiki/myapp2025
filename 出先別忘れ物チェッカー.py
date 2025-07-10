import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = "places_items.json"

# データ読み書き
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 行き先を登録
def register_place():
    place = entry_place.get().strip()
    items = entry_items.get().strip()
    if not place or not items:
        messagebox.showwarning("入力エラー", "行き先と持ち物を入力してください。")
        return
    data[place] = [item.strip() for item in items.split(",")]
    save_data()
    update_listbox()
    messagebox.showinfo("登録完了", f"{place} に持ち物を登録しました。")
    entry_place.delete(0, tk.END)
    entry_items.delete(0, tk.END)

# 持ち物表示
def show_items():
    place = entry_place_query.get().strip()
    show_items_for_place(place)

def show_items_for_place(place):
    items = data.get(place)
    if items:
        result = f"{place} の持ち物:\n" + "\n".join(f"- {item}" for item in items)
    else:
        result = f"{place} に登録された持ち物はありません。"
    label_result.config(text=result)

# 一斉削除
def delete_all_data():
    if messagebox.askyesno("確認", "すべてのデータを削除しますか？"):
        data.clear()
        save_data()
        update_listbox()
        label_result.config(text="")
        messagebox.showinfo("削除完了", "すべてのデータを削除しました。")

# 行き先一覧更新
def update_listbox():
    listbox_places.delete(0, tk.END)
    for place in data:
        listbox_places.insert(tk.END, place)

# 選択削除
def delete_selected_place():
    selection = listbox_places.curselection()
    if not selection:
        messagebox.showwarning("選択エラー", "削除する行き先を選んでください。")
        return
    place = listbox_places.get(selection[0])
    if messagebox.askyesno("確認", f"{place} を削除しますか？"):
        data.pop(place, None)
        save_data()
        update_listbox()
        label_result.config(text="")
        messagebox.showinfo("削除完了", f"{place} を削除しました。")

# ダブルクリックでチェックリスト表示
def on_listbox_double_click(event):
    selection = listbox_places.curselection()
    if selection:
        place = listbox_places.get(selection[0])
        open_checklist_window(place)

# ポップアップ：チェックリスト + 削除機能
def open_checklist_window(place):
    popup = tk.Toplevel()
    popup.title(f"{place} のチェックリスト")

    checklist_vars = {}  # item名: (var, frame)

    checklist_frame = tk.Frame(popup)
    checklist_frame.pack()

    def add_item_to_list(item_name):
        if item_name in checklist_vars:
            return
        var = tk.BooleanVar()
        frame = tk.Frame(checklist_frame)
        cb = tk.Checkbutton(frame, text=item_name, variable=var)
        cb.pack(side="left")

        def delete_item():
            if messagebox.askyesno("確認", f"{item_name} を削除しますか？"):
                frame.destroy()
                checklist_vars.pop(item_name)

        btn = tk.Button(frame, text="×", fg="red", command=delete_item)
        btn.pack(side="right")
        frame.pack(anchor="w", pady=2)
        checklist_vars[item_name] = (var, frame)

    # 既存の持ち物表示
    for item in data.get(place, []):
        add_item_to_list(item)

    # --- 追加欄 ---
    frame_add = tk.Frame(popup)
    frame_add.pack(pady=5)
    tk.Label(frame_add, text="持ち物を追加:").pack(side="left")
    entry_new_item = tk.Entry(frame_add, width=30)
    entry_new_item.pack(side="left")

    def add_new_item():
        new_item = entry_new_item.get().strip()
        if new_item:
            add_item_to_list(new_item)
            entry_new_item.delete(0, tk.END)

    tk.Button(frame_add, text="追加", command=add_new_item).pack(side="left", padx=5)

    # 保存ボタン
    def save_checklist():
        updated_items = list(checklist_vars.keys())
        data[place] = updated_items
        save_data()
        update_listbox()
        messagebox.showinfo("保存完了", f"{place} の持ち物を保存しました。")
        popup.destroy()

    tk.Button(popup, text="保存して閉じる", command=save_checklist).pack(pady=10)

# --- メインUI ---
data = load_data()
root = tk.Tk()
root.title("出先別忘れ物チェッカー")

# 登録
tk.Label(root, text="行き先の登録").pack()
entry_place = tk.Entry(root, width=30)
entry_place.pack()
tk.Label(root, text="持ち物（カンマ区切りで）").pack()
entry_items = tk.Entry(root, width=50)
entry_items.pack()
tk.Button(root, text="登録する", command=register_place).pack(pady=5)

# 検索
tk.Label(root, text="行き先を入力して持ち物を表示").pack(pady=10)
entry_place_query = tk.Entry(root, width=30)
entry_place_query.pack()
tk.Button(root, text="持ち物を表示", command=show_items).pack(pady=5)
label_result = tk.Label(root, text="", justify="left")
label_result.pack()

# 一覧表示
tk.Label(root, text="登録済み行き先一覧（ダブルクリックで開く）").pack(pady=10)
listbox_places = tk.Listbox(root, width=40, height=6)
listbox_places.pack()
listbox_places.bind("<Double-Button-1>", on_listbox_double_click)

tk.Button(root, text="選択した行き先を削除", command=delete_selected_place, fg="red").pack(pady=5)
tk.Button(root, text="⚠️すべてのデータを削除", command=delete_all_data, fg="red").pack(pady=10)

# 初期化
update_listbox()
root.mainloop()


