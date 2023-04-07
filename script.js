// Updates the products' list with the api
async function addAllProducts() {
    let response = await fetch('/api/getAllProductsHTML');
    let allProductsHTML = await response.text();
    document.querySelector('.products-list').insertAdjacentHTML('afterbegin',allProductsHTML)
}

// Adds a fake product to make the last product not centered if necessary
function completeProductsList() {
    let fake = document.querySelector('.fake-product');
    if (fake!=null) fake.remove();
    let products=document.querySelectorAll('.product');
    visibleProducts = [];
    products.forEach(element => {
        if (getComputedStyle(element).display!='none'){
            visibleProducts.push(element);
        }
    });
    if (visibleProducts.length%2==1) {
        fake = document.createElement('div');
        fake.classList.add('product');
        fake.classList.add('fake-product');
        document.querySelector('.products-list').appendChild(fake);
    }
}

function openOrderPopup(product) {
    if (document.querySelector('.priority-background')!=null) document.querySelector('.priority-background').remove();
    if (document.querySelector('.popup')!=null) document.querySelector('.popup').remove();
    const bodyElement = document.querySelector('body');
    let popup = document.createElement('div');
    popup.classList.add('priority-background');
    let orderPopup = document.createElement('form');
    orderPopup.classList.add('order-form');
    orderPopup.classList.add('vertical');
    orderPopup.method = 'post';
    orderPopup.action = '/api/addOrder';
    orderPopup.noValidate = false;
    orderPopup.insertAdjacentHTML('afterbegin', `
    <input type="hidden" value="`+product+`" name="product-name" required>
    <label for="email">Votre email *: </label>
    <input type="email" id="email"  name="email" required>
    <label for="name">Votre nom : </label>
    <input type="text" id="name" name="name">
    <label for="first-name">Votre prénom : </label>
    <input type="text" id="first-name" name="first-name">
    </br>
    <input type="submit" id="order" value="Commander">
    </br>
    </br>
    `);
    popup.appendChild(orderPopup);
    bodyElement.appendChild(popup);
    let closeButton = document.createElement('button');
    closeButton.classList.add('unselectable');
    closeButton.append('Fermer');
    closeButton.onclick = function (){
        document.querySelector('.priority-background').remove();
    }
    orderPopup.appendChild(closeButton);
}

// Opens a central fixed div containing the text of the `content` parameter, with a radial gradient from the #f0f0f0 center to `color`
function openpopup(content,color,productClass) {
    if (document.querySelector('.popup')!=null) document.querySelector('.popup').remove();

    const bodyElement = document.querySelector('body');
    let popup = document.createElement('div');
    popup.classList.add('popup');
    popup.classList.add('vertical');
    popup.classList.add('basic');
    popup.classList.add('medsize');
    popup.classList.add(productClass);
    popup.style.background = 'radial-gradient(circle at center, #f0f0f0, '+color+')';
    popup.append(content);
    let closeButton = document.createElement('button');
    closeButton.classList.add('unselectable');
    closeButton.append('Fermer');
    closeButton.onclick = function (){
        document.querySelector('.popup').remove();
    }
    popup.appendChild(closeButton);
    bodyElement.appendChild(popup);
}


// Code executed after page loads
window.onload = async function() {
    if (document.querySelector('.products-list') != null) {
        await addAllProducts();
        // Synchronize the checkboxes
        var form = document.querySelectorAll('.menu > div');
        for (let i=0; i<form.length; i++){
            form[i].querySelector('div:not(.child-input) input').onchange = function() {
                childInputs = document.querySelectorAll('.menu > div:nth-of-type('+(i+1).toString()+') > div.child-input input');
                if (this.checked){
                    childInputs.forEach(element => {
                        element.checked = true;
                        element.onchange();
                    });
                } else {
                    childInputs.forEach(element => {
                        element.checked = false;
                        element.onchange();
                    });
                }
            }
            form[i].querySelectorAll('div.child-input input').forEach( element => element.onchange = function() {
                parentInput = document.querySelector('.menu > div:nth-of-type('+(i+1).toString()+') > div:not(.child-input) input')
                childInputs = document.querySelectorAll('.menu > div:nth-of-type('+(i+1).toString()+') > div.child-input input');
                childInputsArray = Array.from(childInputs);
                if (childInputsArray.every(i => !(i.checked))){
                    parentInput.checked = false;
                    parentInput.indeterminate = false;
                } else if (childInputsArray.every(i => i.checked)){
                    parentInput.checked = true;
                    parentInput.indeterminate = false;
                } else {
                    parentInput.indeterminate = true;
                }
                // Adds a class to the body element when the checkboxes are checked to assure, with CSS, that all the corresponding planets' display will be set to "none" when not 
                checkedClass = this.getAttribute('id')+'-checked';
                bodyClasses = document.querySelector('body').classList;
                if (bodyClasses.contains(checkedClass)){
                    if (!this.checked) bodyClasses.remove(checkedClass);
                } else {
                    if (this.checked) bodyClasses.add(checkedClass);
                }
                completeProductsList();
            })
        }

        // Complete the checkboxes according to if the page was accessed from the buttons corresponding to the planets or the stars only
        query = window.location.search.substring(1);
        if (query=='planets'){
            planetsInput = document.querySelector('#planets');
            planetsInput.checked = true;
            planetsInput.onchange();
        } else if (query=='stars') {
            starsInput = document.querySelector('#stars');
            starsInput.checked = true;
            starsInput.onchange();
        } else {
            document.querySelectorAll('.menu :not(.child-input) > input[type="checkbox"]').forEach(element => {
                element.checked = true;
                element.onchange();
            });
        }
    }
}