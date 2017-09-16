var colors
document.addEventListener('DOMContentLoaded', function () {
    colors = document.getElementsByClassName('color')

    Array.prototype.forEach.call(colors, function (element, i, a) {
        element.addEventListener('touchstart', function(e) {
            e.target.classList.add('touching')
        })
        element.addEventListener('touchend', function(e) {
            Array.prototype.forEach.call(colors, function (element, i, a) {
                if(element.classList.contains('touched'))
                    element.classList.remove('touched')
                if(e.target === element && element.classList.contains('touching'))
                    e.target.classList.add('touched')
                if(element.classList.contains('touching'))
                    element.classList.remove('touching')
            })
        })
        element.addEventListener('click', function(e) {
            console.log(e)
            let form = new FormData()
            form.append('color', e.srcElement.id)
            fetch('/color', {
                method: 'PUT',
                body: form
            })
        })
        
    })
})
