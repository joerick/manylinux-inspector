interface Standard {
    name: string
    description: string
}

export const standards: Standard[] = [
    {
        name: 'manylinux_2_34',
        description:
            'manylinux_2_34 is the latest of the manylinux standards, with a glibc version of 2.34.' +
            "It's based on AlmaLinux, which is an community-driven Linux distribution that forked from CentOS and RHEL." +
            'Its tag was defined in the generic PEP600.',
    },
    {
        name: 'manylinux_2_28',
        description: "manylinux_2_28 is a previous manylinux standard, with a glibc version of 2.28. It's based on AlmaLinux, which is an community-driven Linux distribution that forked from CentOS and RHEL. Its tag was defined in the generic PEP600.",
    },
    {
        name: 'manylinux_2_24',
        description: "manylinux_2_28 is a previous manylinux standard, with a glibc version of 2.24. It's the only manylinux standard based on Debian. Its tag was defined in the generic PEP600.",
    },
    {
        name: 'manylinux2014',
        description: "manylinux2014 is a manylinux standard with a glibc version of 2.17. It's the final manylinux standard based on CentOS, in this case, CentOS 7. Its policy was defined in PEP599.",
    },
    {
        name: 'manylinux2010',
        description: "manylinux2010 is a manylinux standard with a glibc version of 2.12. The images are based on CentOS 6. Its tag was defined in PEP571.",
    },
    {
        name: 'manylinux1',
        description: "manylinux1 is the first manylinux standard, with a glibc version of 2.5. The images are based on CentOS 5.11. It was defined in PEP513.",
    },
    {
        name: 'musllinux_1_1',
        description: "musllinux_1_1 is a wheel policy that's based on the musl libc, in this case musl v1.1. The images are based on Alpine. It was defined in PEP 656.",
    },
]

export function compareStandardNames(a: string, b: string) {
    const aIndex = standards.findIndex(standard => standard.name == a)
    const bIndex = standards.findIndex(standard => standard.name == b)
    if (aIndex == -1 && bIndex == -1) { return 0 }
    if (aIndex == -1) { return 1 }
    if (bIndex == -1) { return -1 }
    return aIndex - bIndex
}
