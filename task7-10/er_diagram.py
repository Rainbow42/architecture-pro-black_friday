# -*- coding: utf-8 -*-
"""Рисует ER-схему коллекций products, orders, carts в файл er-diagram.png."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

W, H = 17.5, 9.6
fig, ax = plt.subplots(figsize=(W, H), dpi=110)
ax.set_xlim(0, 100); ax.set_ylim(11, 68); ax.axis("off")
fig.patch.set_facecolor("white")

C_HEAD = "#4a6fa5"; C_HEAD_EMB = "#8a8a8a"; C_BODY = "#ffffff"
C_BORDER = "#4a6fa5"; C_BORDER_EMB = "#8a8a8a"; C_TXT = "#1a1a1a"; C_MUTED = "#5c5c5c"
ROW = 1.55; HEAD = 2.0; PAD = 0.45

boxes = {}

def table(key, title, subtitle, fields, x, y, w, embedded=False):
    h = HEAD + ROW * len(fields) + PAD
    border = C_BORDER_EMB if embedded else C_BORDER
    head = C_HEAD_EMB if embedded else C_HEAD
    ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.02,rounding_size=0.25",
                                linewidth=1.6, edgecolor=border, facecolor=C_BODY,
                                linestyle="--" if embedded else "-", zorder=2))
    ax.add_patch(Rectangle((x, y - HEAD), w, HEAD, linewidth=0, facecolor=head, zorder=3))
    ax.text(x + 0.5, y - HEAD / 2 + 0.25, title, va="center", ha="left", fontsize=11.5,
            color="white", weight="bold", zorder=4)
    ax.text(x + 0.5, y - HEAD / 2 - 0.45, subtitle, va="center", ha="left", fontsize=7.6,
            color="#e8eefc", zorder=4)
    yy = y - HEAD - 0.35
    for name, typ, mark in fields:
        weight = "bold" if mark else "normal"
        colr = {"PK": "#1f4e8c", "SK": "#b8860b", "FK": "#4a7a4a", "PK+SK": "#1f4e8c"}.get(mark, "#000000")
        if mark:
            ax.text(x + 0.55, yy - ROW / 2, mark, va="center", ha="left",
                    fontsize=6.6 if len(mark) > 2 else 7.6, color=colr, weight="bold", zorder=4)
        ax.text(x + 3.2, yy - ROW / 2, name, va="center", ha="left",
                fontsize=9.2, color=C_TXT, weight=weight, zorder=4)
        ax.text(x + w - 0.55, yy - ROW / 2, typ, va="center", ha="right",
                fontsize=8.2, color=C_MUTED, style="italic", zorder=4)
        yy -= ROW
    boxes[key] = (x, y - h, w, h)
    return boxes[key]

table("customer", "покупатель", "внешний сервис, отдельной коллекции нет",
      [("customer_id", "UUID", "PK")], 12.0, 66, 20)

table("guest", "гостевой сеанс", "внешний сервис, отдельной коллекции нет",
      [("session_id", "string", "PK")], 68.0, 66, 20)

table("orders", "orders", "ключ шардирования: customer_id (хеш) + created_at",
      [("_id", "ObjectId", "PK"),
       ("customer_id", "UUID", "SK"),
       ("created_at", "Date", "SK"),
       ("status", "string", ""),
       ("total", "Decimal128", ""),
       ("geo_zone", "string", ""),
       ("items", "array", "")], 2.0, 58, 23)

table("carts", "carts", "ключ шардирования: owner_id (хеш)",
      [("_id", "ObjectId", "PK"),
       ("owner_id", "string", "SK"),
       ("owner_type", "string", ""),
       ("user_id", "UUID", "FK"),
       ("session_id", "string", "FK"),
       ("status", "string", ""),
       ("items", "array", ""),
       ("created_at", "Date", ""),
       ("updated_at", "Date", ""),
       ("expires_at", "Date", "")], 74.0, 58, 23)

table("products", "products", "ключ шардирования: category + _id",
      [("_id", "ObjectId", "PK+SK"),
       ("category", "string", "SK"),
       ("name", "string", ""),
       ("price", "Decimal128", ""),
       ("attributes", "object", ""),
       ("stock", "array", ""),
       ("updated_at", "Date", "")], 38.0, 44, 23)

table("order_item", "items (внутри orders)", "вложенный массив",
      [("product_id", "ObjectId", "FK"),
       ("name", "string", ""),
       ("price", "Decimal128", ""),
       ("quantity", "int", "")], 2.0, 26, 23, embedded=True)

table("cart_item", "items (внутри carts)", "вложенный массив",
      [("product_id", "ObjectId", "FK"),
       ("quantity", "int", "")], 74.0, 26, 23, embedded=True)

table("stock", "stock (внутри products)", "вложенный массив",
      [("geo_zone", "string", ""),
       ("quantity", "int", "")], 38.0, 21, 23, embedded=True)

def anchor(k, side):
    x, y, w, h = boxes[k]
    return {"t": (x + w / 2, y + h), "b": (x + w / 2, y),
            "l": (x, y + h - 1.0), "r": (x + w, y + h - 1.0)}[side]

def link(a, sa, b, sb, label, card_a="1", card_b="N", dashed=False, lx=0, ly=0):
    x1, y1 = anchor(a, sa); x2, y2 = anchor(b, sb)
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-", color="#6b6b6b", lw=1.3,
                                linestyle="--" if dashed else "-",
                                connectionstyle="arc3,rad=0"), zorder=1)
    ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontsize=8.4, color="#333333",
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none"), zorder=5)
    ax.text(x1 + (x2 - x1) * 0.08, y1 + (y2 - y1) * 0.08, card_a, fontsize=8, color="#a33", zorder=5)
    ax.text(x1 + (x2 - x1) * 0.92, y1 + (y2 - y1) * 0.92, card_b, fontsize=8, color="#a33", zorder=5)

link("customer", "b", "orders", "t", "оформляет\ncustomer_id", "1", "N", ly=0.3)
link("customer", "r", "carts", "l", "владеет корзиной\nowner_type = user", "1", "0..1", ly=1.2)
link("guest", "b", "carts", "t", "владеет корзиной\nowner_type = guest", "1", "0..1", ly=0.3)
link("orders", "b", "order_item", "t", "содержит", "1", "N", dashed=True, ly=0.2)
link("carts", "b", "cart_item", "t", "содержит", "1", "N", dashed=True, ly=0.2)
link("products", "b", "stock", "t", "содержит", "1", "N", dashed=True, ly=0.2)
link("products", "l", "order_item", "r", "куплен как\nproduct_id", "1", "N", ly=1.0)
link("products", "r", "cart_item", "l", "отложен как\nproduct_id", "1", "N", ly=1.0)

ax.text(50, 67.4, "Схема данных: коллекции products, orders, carts", fontsize=15,
        weight="bold", ha="center", color="#1a1a1a")

leg = ("PK — первичный ключ      SK — поле ключа шардирования      FK — ссылка на другую сущность"
       "      сплошная линия — связь по идентификатору      пунктир — вложенный массив внутри документа")
ax.text(50, 12.2, leg, fontsize=8.6, ha="center", color="#444444")

plt.tight_layout()
plt.savefig("er-diagram.png", dpi=110, facecolor="white", bbox_inches="tight")
print("схема сохранена в er-diagram.png")
