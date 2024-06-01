  // Ініціалізація Slick Carousel після завантаження сторінки
$(document).ready(function(){
    $(".multiple-items").slick({
      dots: true,
      infinite: true,
      speed: 500,
      slidesToShow: 5,
      slidesToScroll: 2
      
    });
});

