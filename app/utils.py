from .models import Product
import pandas as pd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.decomposition import NMF
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors



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


def get_recommendations_NMF(target_customer_id, customers, products, interaction_history, n_recommendations=10):
    # Завантажте дані з InteractionHistory, Customer та Product

    # Перетворіть DataFrame в розріджену матрицю
    interaction_matrix_csr, interaction_matrix = create_sparse_matrix(interaction_history, customers, products)

    # Використайте NMF для розкладання матриці взаємодій
    model = NMF(n_components=6, init='random', random_state=0)
    W = model.fit_transform(interaction_matrix_csr)
    H = model.components_

    # Перемножте матриці W і H, щоб отримати прогнозовані оцінки
    predicted_ratings = np.dot(W, H)

    # Створіть DataFrame з прогнозованими оцінками
    predicted_ratings_df = pd.DataFrame(predicted_ratings, index=interaction_matrix.index, columns=interaction_matrix.columns)

    print("ПРОГНОЗОВАНІ ОЦІНКИ")
    print(predicted_ratings_df)
    
    # Для кожного користувача знайдіть продукти з найвищими прогнозованими оцінками
    recommendations = {}
    for customer_id in predicted_ratings_df.index:
        top_products = predicted_ratings_df.loc[customer_id].nlargest(n_recommendations).index.tolist()
        recommendations[customer_id] = top_products

    # Перевірка наявності цільового користувача
    if target_customer_id not in recommendations:
        print(f"Customer ID {target_customer_id} not found in recommendations.")
        return []

    # Поверніть рекомендації для цільового користувача
    recommended_product_ids = recommendations[target_customer_id]
    return Product.objects.filter(id__in=recommended_product_ids)


def get_recommendations_collaborative_item_item(product, interaction_history, customers, products, k=10, metric='cosine', n_recommendations=10):
    # Створіть DataFrame з історією взаємодій
    interaction_matrix_csr, interaction_matrix = create_sparse_matrix(interaction_history, customers, products)

    user_mapper = {user_id: idx for idx, user_id in enumerate(interaction_matrix.index)}
    item_mapper = {item_id: idx for idx, item_id in enumerate(interaction_matrix.columns)}
    item_inv_mapper = {v: k for k, v in item_mapper.items()}

    # Transpose the interaction matrix for item-item similarity
    interaction_matrix_csr = interaction_matrix_csr.T

    # Get the product index
    product_id = item_mapper[product.id]
    item_vec = interaction_matrix_csr[product_id]

    if isinstance(item_vec, (np.ndarray)):
        item_vec = item_vec.reshape(1, -1)

    # Use k+1 since kNN output includes the itemId of interest
    kNN = NearestNeighbors(n_neighbors=k+1, algorithm="brute", metric=metric)
    kNN.fit(interaction_matrix_csr)

    # Find k-nearest neighbors
    neighbour = kNN.kneighbors(item_vec, return_distance=False)
    neighbour_ids = [item_inv_mapper[neighbour.item(i)] for i in range(1, k+1)]

    # Get the top n recommendations
    # Get the top n recommendations
    recommendations_ids = neighbour_ids[:n_recommendations]

    return Product.objects.filter(id__in=recommendations_ids)
    



def create_sparse_matrix(interaction_history, customers, products):
    # Створіть DataFrame з історією взаємодій
    df = pd.DataFrame(list(interaction_history.values()))
    print("DF ІСТОРІЯ ВЗАЄМОДІЙ")
    print(df)

    # Створіть нульову матрицю взаємодій з розміром (кількість користувачів x кількість продуктів)
    interaction_matrix = pd.DataFrame(np.zeros((len(customers), len(products))), index=[c.id for c in customers], columns=[p.id for p in products])

    print(" ІСТОРІЯ ВЗАЄМОДІЙ НУЛЬОВА МАТРИЦЯ ВЗАЄМОДІЙ")
    print(interaction_matrix)
    
    # Заповніть матрицю взаємодій на основі історії взаємодій
    for _, row in df.iterrows():
        interaction_matrix.loc[row['customer_id'], row['product_id']] = 1

    print("МАТРИЦЯ ВЗАЄМОДІЙ")
    print(interaction_matrix)

    # Перетворіть DataFrame в розріджену матрицю
    interaction_matrix_csr = csr_matrix(interaction_matrix.values)
    return interaction_matrix_csr, interaction_matrix

