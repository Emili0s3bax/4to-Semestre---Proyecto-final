document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('pinterest-container');

    // Función para obtener los posts del backend
    async function fetchPosts() {
        try {
            const response = await fetch('http://localhost:8000/posts');
            const posts = await response.json();
            
            // Limpiar contenedor
            container.innerHTML = '';
            
            posts.forEach(post => {
                const card = document.createElement('div');
                card.className = 'post-card';
                card.innerHTML = `
                    <img src="${post.url}" alt="${post.titulo}">
                    <p>${post.titulo}</p>
                `;

                // --- CORRECCIÓN AQUÍ ---
                // Añadimos el evento directamente a la tarjeta recién creada
                card.addEventListener('click', () => {
                    const imgSrc = post.url; // Usamos el dato directo del post
                    window.location.href = `detalle.html?image=${encodeURIComponent(imgSrc)}`;
                });

                container.appendChild(card);
            });
        } catch (error) {
            console.error('Error cargando posts:', error);
        }
    }

    fetchPosts();
});