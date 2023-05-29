/// <reference types="vite/client" />

declare namespace Intl {
  interface DateTimeFormatOptions {
    dateStyle?: 'full' | 'long' | 'medium' | 'short'
  }
}

declare module 'shell-quote/quote' {
    function quote(args: string[]): string
    export = quote
}
