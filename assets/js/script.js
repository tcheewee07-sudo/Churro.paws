// ===== Gallery images =====
const TOTAL_IMAGES = 38;
const images = Array.from({ length: TOTAL_IMAGES }, (_, i) => {
  const idx = String(i + 1).padStart(2, '0');
  return `assets/images/churro-${idx}.jpg`;
});

const galleryGrid = document.getElementById('galleryGrid');
images.forEach((src, i) => {
  const item = document.createElement('div');
  item.className = 'gallery-item reveal';
  item.dataset.index = i;
  item.innerHTML = `<img src="${src}" alt="Churro photo ${i + 1}" loading="lazy">`;
  galleryGrid.appendChild(item);
});

// ===== Lightbox =====
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');
const lightboxCount = document.getElementById('lightboxCount');
let currentIndex = 0;

function openLightbox(i) {
  currentIndex = i;
  updateLightbox();
  lightbox.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeLightbox() {
  lightbox.classList.remove('open');
  document.body.style.overflow = '';
}
function updateLightbox() {
  lightboxImg.src = images[currentIndex];
  lightboxCount.textContent = `${currentIndex + 1} / ${images.length}`;
}
function nextImage() { currentIndex = (currentIndex + 1) % images.length; updateLightbox(); }
function prevImage() { currentIndex = (currentIndex - 1 + images.length) % images.length; updateLightbox(); }

galleryGrid.addEventListener('click', (e) => {
  const item = e.target.closest('.gallery-item');
  if (item) openLightbox(Number(item.dataset.index));
});
document.getElementById('lightboxClose').addEventListener('click', closeLightbox);
document.getElementById('lightboxNext').addEventListener('click', nextImage);
document.getElementById('lightboxPrev').addEventListener('click', prevImage);
lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener('keydown', (e) => {
  if (!lightbox.classList.contains('open')) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowRight') nextImage();
  if (e.key === 'ArrowLeft') prevImage();
});

// ===== Nav toggle (mobile) =====
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));

// ===== Navbar scroll state =====
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

// ===== Active nav link on scroll =====
const sections = ['home', 'about', 'personality', 'gallery', 'favorites']
  .map(id => document.getElementById(id))
  .filter(Boolean);
const navLinkEls = document.querySelectorAll('.nav-link');
const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinkEls.forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`);
      });
    }
  });
}, { rootMargin: '-45% 0px -45% 0px' });
sections.forEach(s => sectionObserver.observe(s));

// ===== Reveal on scroll =====
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

function observeReveals() {
  document.querySelectorAll('.reveal:not(.in-view)').forEach(el => revealObserver.observe(el));
}
observeReveals();
// gallery items are added dynamically before this runs, but observe again after paint just in case
requestAnimationFrame(observeReveals);
