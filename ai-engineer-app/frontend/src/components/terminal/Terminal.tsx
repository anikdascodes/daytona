import { useEffect, useRef } from 'react'
import { Terminal as XTerm } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

interface TerminalProps {
  output: string[]
  onCommand?: (command: string) => void
}

export function Terminal({ output, onCommand }: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null)
  const xtermRef = useRef<XTerm | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)
  const inputRef = useRef('')
  const lastOutputLengthRef = useRef(0)

  useEffect(() => {
    if (!terminalRef.current) return

    const term = new XTerm({
      cursorBlink: true,
      fontSize: 13,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      theme: {
        background: '#1a1b26',
        foreground: '#a9b1d6',
        cursor: '#c0caf5',
        cursorAccent: '#1a1b26',
        black: '#32344a',
        red: '#f7768e',
        green: '#9ece6a',
        yellow: '#e0af68',
        blue: '#7aa2f7',
        magenta: '#ad8ee6',
        cyan: '#449dab',
        white: '#787c99',
        brightBlack: '#444b6a',
        brightRed: '#ff7a93',
        brightGreen: '#b9f27c',
        brightYellow: '#ff9e64',
        brightBlue: '#7da6ff',
        brightMagenta: '#bb9af7',
        brightCyan: '#0db9d7',
        brightWhite: '#acb0d0',
      },
    })

    const fitAddon = new FitAddon()
    term.loadAddon(fitAddon)
    term.open(terminalRef.current)
    fitAddon.fit()

    xtermRef.current = term
    fitAddonRef.current = fitAddon

    // Handle resize
    const handleResize = () => {
      fitAddon.fit()
    }
    window.addEventListener('resize', handleResize)

    // Handle input
    term.onData((data) => {
      if (data === '\r') {
        // Enter pressed
        term.write('\r\n')
        if (onCommand && inputRef.current.trim()) {
          onCommand(inputRef.current.trim())
        }
        inputRef.current = ''
        term.write('\x1b[32m$\x1b[0m ')
      } else if (data === '\x7f') {
        // Backspace
        if (inputRef.current.length > 0) {
          inputRef.current = inputRef.current.slice(0, -1)
          term.write('\b \b')
        }
      } else if (data >= ' ') {
        inputRef.current += data
        term.write(data)
      }
    })

    // Initial prompt
    term.write('\x1b[32m$\x1b[0m ')

    return () => {
      window.removeEventListener('resize', handleResize)
      term.dispose()
    }
  }, [])

  // Handle output changes
  useEffect(() => {
    if (!xtermRef.current) return

    const newOutput = output.slice(lastOutputLengthRef.current)
    for (const line of newOutput) {
      xtermRef.current.write('\r\n' + line)
    }
    if (newOutput.length > 0) {
      xtermRef.current.write('\r\n\x1b[32m$\x1b[0m ')
    }
    lastOutputLengthRef.current = output.length
  }, [output])

  return (
    <div className="h-full bg-[#1a1b26] rounded-lg overflow-hidden terminal-dark">
      <div ref={terminalRef} className="h-full p-2" />
    </div>
  )
}
