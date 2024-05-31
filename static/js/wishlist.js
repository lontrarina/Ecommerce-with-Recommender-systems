var likeBtns = document.getElementsByClassName('like-btn')

for (var i = 0; i < likeBtns.length; i++) {
    likeBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)
        if (user === 'AnonymousUser') {
            console.log('Not logged in')
        } else {
            updateUserWishlist(productId, action)
        }
    })
}

function updateUserWishlist(productId, action) {
    console.log('User is authenticated, sending data...')

    var url = '/update_wishlist/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action }),
    })

        .then((response) => {
            return response.json()
        })

        .then((data) => {
            console.log('data:', data)
            location.reload()
        })
}
