import { Mutex } from "async-mutex"
import { parseRepoName } from "./nameParsing"

export interface VersionRef {
    domain: string
    org: string
    name: string
    tag: string
    archs: string[]
    filename: string
}

function versionRefImageRegex(versionRef: VersionRef) {
    return new RegExp(`^${versionRef.domain}/${versionRef.org}/${versionRef.name}_(.+):${versionRef.tag}$`)
}

interface IndexJSON {
    versions_reports: VersionRef[],
    latest: {
        metadata: {generated_at: number},
        data: {
            [versionId: string]: string,
        }
    }
}


export class VersionsIndex {
    static instance: VersionsIndex|null = null
    static mutex = new Mutex()
    static async get() {
        return await this.mutex.runExclusive(async () => {
            if (this.instance) {
                return this.instance
            }
            const url = new URL('../data/index.json', import.meta.url)
            const response = await fetch(url.toString())
            const indexJSON = await response.json() as IndexJSON
            this.instance = new VersionsIndex(indexJSON)
            return this.instance
        })
    }

    latestImageIds: string[]
    latest: {[standardName: string]: {[arch: string]: string}}

    constructor(readonly indexJSON: IndexJSON) {
        this.latestImageIds = Object.keys(indexJSON.latest.data).map(imageRepoName => {
            const tag = indexJSON.latest.data[imageRepoName]
            return `${imageRepoName}:${tag}`
        })
        this.latest = {}
        for (const repoName in indexJSON.latest.data) {
            const tag = indexJSON.latest.data[repoName]
            const repoNameParts = parseRepoName(repoName)
            const standardName = repoNameParts.name
            if (!(standardName in this.latest)) {
                this.latest[standardName] = {}
            }
            this.latest[standardName][repoNameParts.arch] = tag
        }
    }

    search(query: string): VersionRef[] {
        const queryLower = query.toLowerCase()
        const queryLowerParts = queryLower.split(',')

        if (queryLower.length < 3) {
            return []
        }

        if (queryLower == 'latest') {
            return this.latestVersionRefs
        }

        if (queryLower == 'all') {
            return this.allVersionRefs
        }

        return this.indexJSON.versions_reports.filter(versionRef => {
            const versionId = `${versionRef.domain}/${versionRef.org}/${versionRef.name}:${versionRef.tag}`
            const versionIdLower = versionId.toLowerCase()
            if (queryLowerParts.some(part => versionIdLower.includes(part))) {
                return true
            }
        })
    }

    latestInfo(version: VersionRef): string | undefined {
        const latestTagByArch = this.latest[version.name]
        if (!latestTagByArch) {
            return undefined
        }

        const latestArchs = [...Object.keys(latestTagByArch)]

        if (latestArchs.every(arch => latestTagByArch[arch] == version.tag)) {
            return 'latest'
        }
        const archsForWhomThisVersionIsLatest = latestArchs.filter(arch => latestTagByArch[arch] == version.tag)
        if (archsForWhomThisVersionIsLatest.length > 0) {
            return `latest for ${archsForWhomThisVersionIsLatest.join(', ')}`
        }
        return undefined
    }

    get allVersionRefs(): VersionRef[] {
        return this.indexJSON.versions_reports
    }

    get latestVersionRefs(): VersionRef[] {
        return this.indexJSON.versions_reports.filter(versionRef => {
            // in the middle of the latest image id is the arch, but versions
            // aren't limited to just one arch.
            // const prefix = `${versionRef.domain}/${versionRef.org}/${versionRef.name}_`
            // const suffix = `:${versionRef.tag}`
            const regex = versionRefImageRegex(versionRef)

            return this.latestImageIds.some(imageId => {
                return regex.test(imageId)
                // return imageId.startsWith(prefix) && imageId.endsWith(suffix)
            })
        })
    }
}

