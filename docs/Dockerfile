FROM nginx:alpine

# Statik dosyalar (index.html, css/, js/, vendor/, data/) doğrudan Nginx'in
# varsayılan kök dizinine kopyalanır. Python/Streamlit runtime GEREKMEZ.
COPY . /usr/share/nginx/html

EXPOSE 80
