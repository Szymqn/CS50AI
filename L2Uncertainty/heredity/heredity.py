import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    entire_joint_probability = 1
    children_to_check = people.keys()

    for child in children_to_check:
        if child not in (one_gene | two_genes | have_trait):
            entire_joint_probability *= PROBS["gene"][0] * PROBS["trait"][0][False]

    if two_genes:
        for _ in two_genes:
            entire_joint_probability *= PROBS["gene"][2] * PROBS["trait"][2][True]

    if one_gene:
        for _ in one_gene:
            entire_joint_probability *= ((1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]) * PROBS["trait"][1][False]

    return entire_joint_probability


def update_trait(num_of_copies, logic_sign, p):
    return PROBS["trait"][num_of_copies][logic_sign] + p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    if one_gene:
        for child in one_gene:
            probabilities[child]["gene"][1] = PROBS["gene"][1] + p
            if child in have_trait:
                probabilities[child]["trait"][True] = update_trait(1, True, p)
            else:
                probabilities[child]["trait"][False] = update_trait(1, False, p)

    if two_genes:
        for child in two_genes:
            probabilities[child]["gene"][2] = PROBS["gene"][2] + p
            if child in have_trait:
                probabilities[child]["trait"][True] = update_trait(2, True, p)
            else:
                probabilities[child]["trait"][False] = update_trait(2, False, p)

    children_to_check = probabilities.keys()

    for child in children_to_check:
        if child not in (one_gene | two_genes | have_trait):
            probabilities[child]["gene"][0] = PROBS["gene"][0] + p
            if child in have_trait:
                probabilities[child]["trait"][True] = update_trait(0, True, p)
            else:
                probabilities[child]["trait"][False] = update_trait(0, False, p)


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for child in probabilities:
        total_gene = sum(probabilities[child]["gene"].values())
        for idx, gene in enumerate(probabilities[child]["gene"].values()):
            probabilities[child]["gene"][idx] /= total_gene

        total_trait = sum(probabilities[child]["trait"].values())
        for idx, trait in enumerate(probabilities[child]["trait"].values()):
            probabilities[child]["trait"][idx] /= total_trait


if __name__ == "__main__":
    main()
