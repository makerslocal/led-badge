var colors
document.addEventListener('DOMContentLoaded', () => {
    colors = document.querySelectorAll('.color')

    for(let element of colors) {
        element.addEventListener('touchstart', function(e) {
            e.target.classList.add('touching')
        })
        element.addEventListener('touchend', function(e) {
            for(let element of colors) {
                if(element.classList.contains('touched'))
                    element.classList.remove('touched')
                if(e.target === element && element.classList.contains('touching'))
                    e.target.classList.add('touched')
                if(element.classList.contains('touching'))
                    element.classList.remove('touching')
            }
        })
        element.addEventListener('click', function(e) {
            console.log(e)
            var form = new FormData()
            form.append('color', e.srcElement.id)
            fetch('/color', {
                method: 'PUT',
                body: form
            })
        })
    }
})
