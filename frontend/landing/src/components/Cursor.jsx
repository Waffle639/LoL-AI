import { useCursor } from '../hooks'

export default function Cursor() {
  useCursor()
  return (
    <>
      <div id="cursor-hex" />
      <div id="cursor-dot" />
    </>
  )
}