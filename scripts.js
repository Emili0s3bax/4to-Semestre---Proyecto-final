$(document).ready(function() {
    const container = $('#pinterest-container');

    // Función para obtener los posts del backend
    async function fetchPosts() {
        try {
            const response = await fetch('http://localhost:8000/posts');
            const posts = await response.json();
            
            // Limpiar contenedor
            container.empty();
            
            posts.forEach(post => {
                // Creamos el elemento usando jQuery
                const card = $('<div>').addClass('post-card');
                
                // Agregamos la imagen con la clase .pin-img para que el selector funcione
                card.html(`
                    <img src="${post.url}" alt="${post.titulo}" class="pin-img">
                    <p>${post.titulo}</p>
                `);

                // Evento de clic usando jQuery
                card.on('click', function() {
                    const imgSrc = post.url;
                    window.location.href = `detalle.html?image=${encodeURIComponent(imgSrc)}`;
                });

                container.append(card);
            });
        } catch (error) {
            console.error('Error cargando posts:', error);
        }
    }

    fetchPosts();
});
