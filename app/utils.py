from .models import Product
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


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


def get_similar_products_content_based(product, n_recommendations=10):
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
    #print(sim_scores)

    similar_products = [indexes[i[0]] for i in sim_scores]
   # print(similar_products)
    # Повертаємо схожі товари
    return Product.objects.filter(name__in=similar_products)




# TF-IDF--------------------------------------------------------------
def get_similar_produc_tfidf(product, n_recommendations=7):
    products = Product.objects.all()
    descriptions = [p.description for p in products]
    product_names = [p.name for p in products]

    # Створюємо матрицю TF-IDF для описів товарів
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(descriptions)
    
    # Обчислюємо косинусну подібність між описами
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # Створюємо DataFrame для зручного відображення
    df = pd.DataFrame(cosine_sim, index=product_names, columns=product_names)
    
    # Знаходимо індекс поточного товару
    if product.name in df.index:
        idx = df.index.get_loc(product.name)
    else:
        return Product.objects.none()  # Повертаємо порожній queryset, якщо товар не знайдено

    # Отримуємо оцінки подібності
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Виключаємо поточний товар з рекомендацій
    sim_scores = sim_scores[1:n_recommendations+1]
    
    similar_product_indices = [score[0] for score in sim_scores]
    similar_products = [products[i] for i in similar_product_indices]
    
    return similar_products