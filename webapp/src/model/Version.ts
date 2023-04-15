import type { Field, ImageReportJSON } from "./ImageReport"
import ImageReport from "./ImageReport"
import { cachedProperty, compareArchs, summariseValues } from "./util"

export default class Version {
    reports: {[arch: string]: ImageReport} = {}
    static async get(domain: string, org: string, name: string, tag: string, signal?: AbortSignal) {
        const versionFilename = `${domain}_${org}_${name}_${tag}.json`
        return await this.getWithFilename(versionFilename, signal)
    }
    static async getWithFilename(filename: string, signal?: AbortSignal) {
        const versionURL = new URL(`../data/versions/${filename}`, import.meta.url)
        const response = await fetch(versionURL.toString(), {signal})
        const versionJSON = await response.json() as VersionJSON
        return new Version(versionJSON)
    }

    constructor(readonly versionJSON: VersionJSON) {
        this.reports = {}
        for (const arch of Object.keys(versionJSON.reports_by_arch)) {
            const reportJSON = versionJSON.reports_by_arch[arch]
            this.reports[arch] = new ImageReport(reportJSON)
        }
    }

    get domain(): string { return this.versionJSON.metadata.domain }
    get org(): string { return this.versionJSON.metadata.org }
    get name(): string { return this.versionJSON.metadata.name }
    get tag(): string { return this.versionJSON.metadata.tag }

    get archs(): string[] {
        const archs = Object.keys(this.reports)
        archs.sort(compareArchs)
        return archs
    }

    _fields?: Field[]
    get fields(): Field[] {
        if (this._fields) return this._fields

        const fieldsById = new Map<string, {[arch: string]: Field}>()
        for (const arch of Object.keys(this.reports)) {
            const report = this.reports[arch]
            for (const field of report.fields) {
                if (!fieldsById.has(field.id)) {
                    fieldsById.set(field.id, {})
                }
                fieldsById.get(field.id)![arch] = field
            }
        }
        const fields: Field[] = []
        for (const fieldsByArch of fieldsById.values()) {
            const valuesByArch: {[arch: string]: string} = {}
            for (const arch of Object.keys(fieldsByArch)) {
                valuesByArch[arch] = fieldsByArch[arch].value ?? 'None'
            }
            const firstArch = Object.keys(fieldsByArch)[0]
            const id = fieldsByArch[firstArch].id
            const label = fieldsByArch[firstArch].label
            const value = summariseValues(valuesByArch)
            fields.push({id, label, value})
        }
        this._fields = fields
        return fields
    }
}

interface VersionJSON {
    metadata: {
        domain: string,
        org: string,
        name: string,
        tag: string,
    },
    reports_by_arch: {
        [arch: string]: ImageReportJSON,
    },
}
