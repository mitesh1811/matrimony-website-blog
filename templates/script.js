
    const text = "Traditional Values. Modern Matches.";
    let i = 0;
    function typeWriter() {
      if (i < text.length) {
        document.getElementById("typeText").innerHTML += text.charAt(i);
        i++;
        setTimeout(typeWriter, 90);
      }
    }
    typeWriter();

    // Dark Mode Toggle
    function toggleMode() {
      document.body.classList.toggle("dark-mode");
    }
  const sections = document.querySelectorAll('section');

  // List of animation classes
  const animations = [
    'zoom-in',
    'slide-left',
    'slide-right',
    'fade-in-up',
    'rotate-in',
    'bounce-in'
  ];

  // Assign random animation to each section
  sections.forEach(section => {
    const animation = animations[Math.floor(Math.random() * animations.length)];
    section.classList.add(animation);
  });

  // Intersection Observer to trigger animations
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        obs.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15
  });

  sections.forEach(section => {
    observer.observe(section);
  });

  
    function thankUser() {
      alert("Thanks for contacting us! We'll get back to you soon.");
    }

    function highlightInput(el) {
      el.style.backgroundColor = "#fffde7";
    }

    function resetHighlight(el) {
      el.style.backgroundColor = "#fff";
    }

    function validateName(el) {
      if (el.value.length < 3) {
        alert("Name should be at least 3 characters.");
        el.focus();
      }
    }