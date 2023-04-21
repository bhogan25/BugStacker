export function setAllDisplayProps(element, display) {

  const displays = [
    'inline',
    'block',
    'flex',
    'grid',
    'inline-block',
    'inline-flex',
    'inline-grid',
    'none',
  ]

  // Check arguments
  if (!(element instanceof HTMLElement) & !(element instanceof SVGElement)) {
    throw new Error('Element must be an instance of an "HTMLElement" or "SVGElement.');
  }

  if (typeof display !== 'string') {
    throw new Error('display property must be a string.');
  }

  if (!displays.includes(display)) {
    throw new Error(`display type "${display}" not allowed.`);
  }

  // Set target element display
  element.style.display = display;

  const children = element.children;

  for (let i = 0; i < children.length; i++) {
    setAllDisplayProps(children[i], display)
  }
}


function returnProjectBodyObject(action, target) {
  if (action.lower() === 'change_status') {
    return { status: target.dataset.status }
  }

  if (action.lower() === 'complete') {
    return {}
  }
}