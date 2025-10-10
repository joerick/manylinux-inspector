export interface RepoNameParts {
    domain: string;
    org: string;
    name: string;
    arch: string;
}

export function parseRepoName(repoName: string): RepoNameParts {
    const regex = /^(?<domain>.*)\/(?<org>.*)\/(?<name>[a-z]*(?:\d|\d\d\d\d|(?:_\d+)+))(?:_(?<arch>.*))?$/;
    const match = regex.exec(repoName);
    if (!match || !match.groups) {
        throw new Error(`Repo name ${repoName} does not match regex ${regex}`);
    }

    const parts = match.groups;

    const domain = parts.domain;
    const org = parts.org;
    const name = parts.name;
    const arch = parts.arch || 'multiarch';

    if (!domain || !org || !name) {
        throw new Error(`Repo name ${repoName} is missing parts`);
    }

    return { domain, org, name, arch };
}
