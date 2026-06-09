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
    const card = $('<div>').addClass('post-card');
    
    // Crear elemento img con manejo de error
    const img = $('<img>')
        .attr('src', post.url)
        .attr('alt', post.titulo)
        .addClass('pin-img')
        .on('error', function() {
            $(this).attr('src', 'ruta/a/imagen_por_defecto.png'); // Imagen si falla la carga
            console.error('No se pudo cargar la imagen:', post.url);
        });

    card.append(img);
    card.append(`<p>${post.titulo}</p>`);

    card.on('click', function() {
        window.location.href = `detalle.html?image=${encodeURIComponent(post.url)}`;
    });

    container.append(card);
});
        } catch (error) {
            console.error('Error cargando posts:', error);
        }
    }

    fetchPosts();
});
