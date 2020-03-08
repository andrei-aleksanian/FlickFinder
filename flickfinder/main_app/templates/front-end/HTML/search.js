const movies = [
    {name: 'American Psycho'},
    {name: 'Joker'},
    {name: 'Fight Club'},
    {name: 'Interstellar'},
    {name: 'Shrek'},
    {name: 'Shrek 2'},
    {name: 'Shrek 3'}
];

const list = document.getElementById('list');

function setList(group) {
    clearList();
    for (const movie of group) {
        const item = document.createElement('li');
        const text = document.createTextNode(movie.name);
        item.appendChild(text);
        list.appendChild(item);
    }
    if (group.length === 0) {
        showNoResults();
    }
};

function clearList(){
    while (list.firstChild){
        list.removeChild(list.firstChild);
    }
}

function showNoResults(){
    const item = document.createElement('li');
    const text = document.createTextNode('No results found');
    item.appendChild(text);
    list.appendChild(item);
}

function getRelevancy(value, searchTerm){
    if (value === searchTerm){
        return 3;
    } else if (value.startsWith(searchTerm)){
        return 2;
    } else if (value.includes(searchTerm)){
        return 1;
    }
}

const searchInput = document.getElementById('search');

searchInput.addEventListener('input', (event)=> {
    let value = event.target.value;
    if (value && value.trim().length > 0) {
        //value = value.trim().toLowerCase();
        setList(movies.filter(movie =>{
            return movie.name.includes(value);
        }).sort((movieA, movieB) => {
            return getRelevancy(movieB.name, value) - getRelevancy(movieA.name, value);

        }));
    }else{
        clearList();
    }
});






