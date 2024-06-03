from .models import Product
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

def create_style_matrix():
    products = Product.objects.all()
    style_set = set()

    # Отримання унікальних стилів
    for product in products:
        styles = product.styles.split("/")
        for style in styles:
            style_set.add(style)

    style_list = sorted(list(style_set))

    # Створення порожньої матриці
    matrix = []
    product_names = []
    for product in products:
        row = [0] * len(style_list)
        product_styles = product.styles.split("/")
        for style in product_styles:
            if style in style_list:
                row[style_list.index(style)] = 1
        matrix.append(row)
        product_names.append(product.name)

    # Створення DataFrame для зручного відображення
    df = pd.DataFrame(matrix, columns=style_list, index=product_names)
    return df


def get_similar_products(product, n_recommendations=10):
    df = create_style_matrix()
    cosine_sim = cosine_similarity(df, df)
    indexes = pd.Series(df.index)
    
    # Знаходимо індекс товару
    idx = indexes[indexes == product.name].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Виключаємо поточний товар з рекомендацій
    sim_scores = [score for score in sim_scores if indexes[score[0]] != product.name]
    sim_scores = sim_scores[:n_recommendations]
    print(sim_scores)

    similar_products = [indexes[i[0]] for i in sim_scores]
    print(similar_products)
    # Повертаємо схожі товари
    return Product.objects.filter(name__in=similar_products)



