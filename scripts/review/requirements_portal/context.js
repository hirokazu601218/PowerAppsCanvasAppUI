/* Only whitelisted local IDs can change the return link. No arbitrary redirect. */
(() => {
  const script = document.querySelector('script[data-portal-root]');
  if (!script) return;

  const portalRoot = new URL(
    script.dataset.portalRoot.replace(/\/?$/, '/'),
    location.href,
  );
  const context = new URLSearchParams(location.search).get('context') || '';
  let destination = '';
  let label = '';

  if (/^section-\d+(?:\.\d+){0,2}$/.test(context)) {
    const sectionId = context.slice(8);
    destination = `sections/${sectionId}.html#section-${sectionId}`;
    label = `元の要件（資料ID ${sectionId}）へ戻る`;
  } else if (/^template-\d+(?:\.\d+){1,2}$/.test(context)) {
    const sectionId = context.slice(9);
    destination = `template-sections/${sectionId}.html#template-${sectionId}`;
    label = `元の原本補完要件 ${sectionId} へ戻る`;
  } else if (/^req-[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(context)) {
    const requirementId = context.slice(4);
    destination = `requirements/${requirementId}.html#requirement-${requirementId}`;
    label = `元の要件 ${requirementId} へ戻る`;
  } else if (/^flow-WF-\d{2}$/.test(context)) {
    const workflowId = context.slice(5);
    destination = `workflows/${workflowId}.html#${workflowId}`;
    label = `元の業務 ${workflowId} へ戻る`;
  } else if (/^screen-[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(context)) {
    const screenId = context.slice(7);
    destination = `screens/${screenId}.html#${screenId}`;
    label = `元の画面 ${screenId} へ戻る`;
  }
  if (!destination) return;

  for (const link of document.querySelectorAll('[data-context-return]')) {
    link.href = new URL(destination, portalRoot).href;
    link.textContent = `← ${label}`;
  }

  // Keep the original context through related, same-origin source documents.
  // Without JavaScript their normal hrefs and static backlinks still work.
  for (const link of document.querySelectorAll('a[data-keep-context]')) {
    const target = new URL(link.href, location.href);
    if (target.origin !== location.origin) continue;
    target.searchParams.set('context', context);
    link.href = target.href;
  }
})();
