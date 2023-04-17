import { isEqual, flatMap, sortBy } from 'lodash'
import { version } from 'vue'
import { dateFromImageTag, formatList, regexExtract } from './util'

export interface ImageReportJSON {
    metadata: {
        image: string,
        generated_at: number,
    }
    data: {
        log: LogEntry[],
    }
}

export interface LogEntry {
    command: string[]
    stdout: string
    stderr: string
    return_code: number
}

export interface Field {
    id: string
    label: string
    value: string | null
}

type OutputPart = 'stdout' | 'stderr' | 'all'

export default class ImageReport {
    constructor(readonly reportJSON: ImageReportJSON) {
        if (!reportJSON.data.log) {
            throw new Error('missing log ' + reportJSON.metadata.image)
        }
    }

    get metadata() { return this.reportJSON.metadata }

    get pythonEnvironments(): PythonEnvironment[] {
        const pythons = new Set<string>()
        for (const logEntry of this.reportJSON.data.log) {
            const program = logEntry.command[0]
            if (program.endsWith('/bin/python')) {
                pythons.add(program)
            }
        }
        return Array.from(pythons.values()).map(path => new PythonEnvironment(this, path))
    }

    get globalTools(): [string, string][] {
        const results = new Map<string, string>()

        const pipxListOutput = this._getCommandOutput(['pipx', 'list', '--short'])?.trim()
        if (pipxListOutput) {
            const lines = pipxListOutput?.split('\n') ?? []
            for (const line of lines) {
                const [name, version] = line.split(' ', 2)
                results.set(name, version)
            }
        }

        const optionalSet = (key: string, value: string | null) => {
            if (value) {
                results.set(key, value)
            }
        }
        optionalSet(
            "auditwheel",
            regexExtract(this._getCommandOutput(['auditwheel', '--version']), /auditwheel (\S+)/)
        )
        optionalSet(
            "patchelf",
            regexExtract(this._getCommandOutput(['patchelf', '--version']), /patchelf (\S+)/)
        )
        optionalSet(
            "git",
            regexExtract(this._getCommandOutput(['git', '--version']), /git version (\S+)/)
        )
        optionalSet(
            "curl",
            regexExtract(this._getCommandOutput(['curl', '--version']), /curl (\S+)/)
        )
        optionalSet(
            "openssl",
            regexExtract(this._getCommandOutput(['openssl', 'version']), /OpenSSL (\S+)/)
        )
        optionalSet(
            "pipx",
            regexExtract(this._getCommandOutput(['pipx', '--version']), /(\S+)/)
        )

        return Array.from(results.entries())
    }

    get operatingSystemRelease(): string | null {
        const osRelease = this._getCommandOutput(['cat', '/etc/os-release'])
        if (osRelease) {
            // os release is key-value pairs in shell var format
            const match = osRelease.match(/PRETTY_NAME=(.*)/)

            if (!match) return osRelease

            let prettyName = match[1]
            // trim
            prettyName = prettyName.trim()

            if (prettyName.startsWith('"')) {
                prettyName = prettyName.slice(1)
                if (prettyName.endsWith('"')) {
                    prettyName = prettyName.slice(0, prettyName.length - 1)
                }
            }
            return prettyName
        }
        return this._getCommandOutput(['cat', '/etc/redhat-release'])?.trim() ?? null
    }

    get operatingSystemLibc(): string | null {
        const libcVersion = this._getCommandOutput(["ldd", "--version"], { part: 'all', allowFail: true })
        // return the first line
        return libcVersion?.split('\n')[0].trim() ?? null
    }

    get operatingSystemPackageManager(): string | null {
        const potentialPackageManagers = [
            "dnf",
            "yum",
            "apt-get",
            "apk",
            "pacman",
            "zypper",
            "emerge",
        ]
        const installedPackageManagers = potentialPackageManagers.filter(name =>
            !!this._getCommandOutput(['which', name])
        )
        return installedPackageManagers.join(', ') || null
    }

    _getCommandOutput(command: string[], options: { part?: OutputPart, allowFail?: boolean } = {}): string | null {
        const { part = 'stdout', allowFail = false } = options

        for (const logEntry of this.reportJSON.data.log) {
            if (isEqual(logEntry.command, command)) {
                if (logEntry.return_code != 0 && !allowFail) {
                    return null
                }

                if (part == 'all') {
                    return logEntry.stdout + logEntry.stderr
                } else {
                    return logEntry[part]
                }
            }
        }
        return null
    }

    get fields(): Field[] {
        return [
            { id: 'os', label: 'OS', value: this.operatingSystemRelease },
            { id: 'os.libc', label: 'libc', value: this.operatingSystemLibc },
            { id: 'os.packageManager', label: 'Package manager', value: this.operatingSystemPackageManager },
            ...flatMap(this.pythonEnvironments, python => python.fields),
            { id: 'global-tools', label: 'Global Tools', value: '' },
            ...this.globalTools.map(([name, version]) => ({
                id: `global-tools.${name}`, label: name, value: version
            })),
        ]
    }
}

export class PythonEnvironment {
    constructor(readonly report: ImageReport, readonly path: string) {
    }

    get identifier(): string {
        // paths look like /opt/python/cp37-cp37m/bin/python
        const pathParts = this.path.split('/')
        return pathParts[3]
    }

    get prettyName(): { name: string, variant?: string } {
        const identifier = this.identifier
        let match = identifier.match(/^([cp]p)(\d)(\d+).*/)
        if (!match) {
            console.warn('unknown python environment identifier', identifier)
            return { name: identifier }
        }

        const interpreterId = match[1]
        const major = match[2]
        const minor = match[3]

        let interpreter
        if (interpreterId == 'cp') {
            interpreter = 'CPython'
        } else if (interpreterId == 'pp') {
            interpreter = 'PyPy'
        } else {
            console.warn('unknown interpreterId', interpreterId)
            interpreter = interpreterId
        }

        let variant

        if (major == '2' && minor == '7') {
            // get the letters at the end of the id
            variant = this.identifier.match(/[a-z]+$/)![0]
        }

        return { name: `${interpreter} ${major}.${minor}`, variant }
    }

    get pythonVersion(): string | null {
        const versionOutput = this._getPythonOutput(['--version'], { part: 'all' })
        return versionOutput?.split(' ')?.[1] ?? null
    }

    get toolVersions(): [string, string][] {
        const result: [string, string][] = []

        const pipVersionOutput = this._getPythonOutput(['-m', 'pip', '--version'])
        const pipVersion = pipVersionOutput?.split(' ')[1]
        if (pipVersion) {
            result.push(['pip', pipVersion])
        }

        const setuptoolsVersionOutput = this._getPythonOutput([
            "-c", "import setuptools; print(setuptools.__version__)"
        ])
        if (setuptoolsVersionOutput) {
            result.push(['setuptools', setuptoolsVersionOutput.trim()])
        }

        const pipFreezeOutput = this._getPythonOutput(['-m', 'pip', 'freeze'])
        if (pipFreezeOutput) {
            for (const line of pipFreezeOutput?.trim().split('\n')) {
                const [packageName, version] = line.split('==')
                result.push([packageName, version])
            }
        }

        return result
    }

    get fields(): Field[] {
        let labelHTML = this.prettyName.name
        if (this.prettyName.variant) {
            labelHTML += `<span class="variant">${this.prettyName.variant}</span>`
        }
        return [
            { id: `python.${this.identifier}`, label: labelHTML, value: this.pythonVersion },
            ...this.toolVersions.map(([name, version]) => {
                return { id: `python.${this.identifier}.${name}`, label: name, value: version }
            })
        ]
    }

    _getPythonOutput(command: string[], options: Parameters<ImageReport["_getCommandOutput"]>[1] = {}): string | null {
        return this.report._getCommandOutput([this.path, ...command], options)
    }
}

export function sortFields<T extends {id: string}>(fields: ArrayLike<T>|Iterable<T>) {
    const regex = /python\.(\w*?)(\d)(\d+)-(.*)/

    const annotatedFields = Array.from(fields).map(field => {
        const keypath = field.id
        const match = keypath.match(regex)
        if (!match) return { field, keypath, priority: !field.id.startsWith('os') }
        return {
            field,
            keypath,
            interpreter: match[1],
            major: -parseInt(match[2]),
            minor: -parseInt(match[3]),
            rest: match[4],
        }
    })

    return sortBy(annotatedFields, ['priority', 'interpreter', 'major', 'minor', 'rest', 'keypath']).map(item => item.field)
}
