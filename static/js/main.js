// selector
const toggleDark = document.querySelector("#toggle-dark");

// state
const theme = localStorage.getItem('theme');

// on mount 
theme && document.body.classList.add(theme); // like an if statement

// handlers
handleThemeToggle =() => {
    document.body.classList.toggle('dark-mode');
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark-mode');
    } else {
        localStorage.removeItem('theme');
    }
};

// events
toggleDark.addEventListener('click', handleThemeToggle);