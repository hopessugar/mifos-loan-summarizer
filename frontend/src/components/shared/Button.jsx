export function Button({ children, onClick, disabled, variant, className }) {
  const base = 'px-4 py-2 rounded-lg font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
  
  let variantClass = 'bg-blue-600 text-white hover:bg-blue-700'
  if (variant === 'secondary') {
    variantClass = 'bg-gray-100 text-gray-700 hover:bg-gray-200'
  }

  const finalClass = base + ' ' + variantClass + ' ' + (className || '')

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={finalClass}
    >
      {children}
    </button>
  )
}