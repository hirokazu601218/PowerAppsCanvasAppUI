/* Static HTML is the primary interface. These controls only enhance it. */
(() => {
  const searchForm = document.querySelector('[data-search-form]');

  if (searchForm) {
    const searchInput = searchForm.querySelector('[name=q]');
    const stateFilter = searchForm.querySelector('[name=state]');
    const kindFilter = searchForm.querySelector('[name=kind]');
    const searchItems = [...document.querySelectorAll('[data-search-item]')];
    const resultMessage = document.querySelector('[data-result-count]');
    const emptyMessage = document.querySelector('[data-empty]');
    const parameters = new URLSearchParams(location.search);

    searchInput.value = parameters.get('q') || '';
    if (stateFilter) stateFilter.value = parameters.get('state') || '';
    if (kindFilter) kindFilter.value = parameters.get('kind') || '';

    function applyFilters() {
      const terms = searchInput.value
        .normalize('NFKC')
        .toLowerCase()
        .trim()
        .split(/\s+/)
        .filter(Boolean);
      let visibleCount = 0;

      for (const item of searchItems) {
        const searchableText = (item.dataset.searchText || item.textContent)
          .normalize('NFKC')
          .toLowerCase();
        const matchesText = terms.every(term => searchableText.includes(term));
        const matchesState = !stateFilter?.value ||
          (item.dataset.states || '').split(' ').includes(stateFilter.value);
        const matchesKind = !kindFilter?.value ||
          item.dataset.kind === kindFilter.value;
        const visible = matchesText && matchesState && matchesKind;

        item.hidden = !visible;
        if (visible) visibleCount += 1;
      }

      resultMessage.textContent = `${searchItems.length}件中 ${visibleCount}件を表示`;
      if (emptyMessage) emptyMessage.hidden = visibleCount !== 0;

      for (const group of document.querySelectorAll('[data-search-group]')) {
        const children = [...group.querySelectorAll('[data-search-item]')];
        group.hidden = !children.some(item => !item.hidden);
      }
    }

    searchForm.addEventListener('submit', event => {
      event.preventDefault();
      applyFilters();
    });
    searchForm.addEventListener('input', applyFilters);
    searchForm.addEventListener('change', applyFilters);
    searchForm.querySelector('[data-reset]').addEventListener('click', () => {
      searchInput.value = '';
      if (stateFilter) stateFilter.value = '';
      if (kindFilter) kindFilter.value = '';
      applyFilters();
      searchInput.focus();
    });
    applyFilters();
  }

  for (const figure of document.querySelectorAll('[data-figure]')) {
    const canvas = figure.querySelector('.diagram-canvas');
    const viewport = figure.querySelector('.diagram-viewport');
    const zoomLabel = figure.querySelector('output');
    const zoomOut = figure.querySelector('[data-zoom-out]');
    const zoomIn = figure.querySelector('[data-zoom-in]');
    let zoom = 1;

    function renderZoom() {
      canvas.style.width = `${zoom * 100}%`;
      zoomLabel.textContent = `${Math.round(zoom * 100)}%`;
      zoomOut.disabled = zoom <= 1;
      zoomIn.disabled = zoom >= 4;
    }

    zoomIn.addEventListener('click', () => {
      zoom = Math.min(4, zoom + 0.5);
      renderZoom();
    });
    zoomOut.addEventListener('click', () => {
      zoom = Math.max(1, zoom - 0.5);
      renderZoom();
    });
    figure.querySelector('[data-zoom-fit]').addEventListener('click', () => {
      zoom = 1;
      renderZoom();
      viewport.scrollTo(0, 0);
    });
    viewport.addEventListener('keydown', event => {
      if (event.target !== viewport) return;
      const directions = {
        ArrowLeft: [-80, 0],
        ArrowRight: [80, 0],
        ArrowUp: [0, -80],
        ArrowDown: [0, 80],
      };
      const offset = directions[event.key];
      if (!offset) return;
      event.preventDefault();
      viewport.scrollBy(...offset);
    });
    renderZoom();
  }

  for (const button of document.querySelectorAll('[data-print]')) {
    button.addEventListener('click', () => window.print());
  }
})();
