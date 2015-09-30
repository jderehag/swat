/**
 * Todo proper typing support
 */

declare module C3 {

  export interface Base {
    generate(options:Options): ChartAPI
  }

  export interface Options extends ChartOpts {
    data: DataOpts
    axis?: any//AxisOpts
    grid?: GridOpts
  }


  export interface ChartOpts {
    bindto?: HTMLElement
    size?: {
      width?: number
      heigth?: number
    }
    padding?: {
      top?: number
      bottom?: number
      left?: number
      right?: number
    }
  }

  export interface DataOpts {
    columns?: any[]
    types?: {
      [key:string]: string
    }
    x?: string
    xs?: {
      [key:string]: string
    }
    axes?: {}
  }

  export interface AxisOpts {
    x?: {
      tick?: {
        format?: Function
      }
    }
    y?: {}
    y2?: {
      show?: Boolean
    }
  }


  export interface GridOpts {
    x?: {
      show?: Boolean
      lines?: any[]
    }
    y?: {
      show: Boolean
      lines?: any[]
    }
    focus?: {show: Boolean}
    lines?: {front: Boolean}
  }

  /**
   * The returned object from calling c3.generate()
   */
  export interface ChartAPI {
    load?:any
    unload?:any
  }
}

declare var c3:C3.Base

