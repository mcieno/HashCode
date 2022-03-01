package main

import (
	"bufio"
	"fmt"
	"strconv"
	"strings"
)

type (
	Problem struct {
		Contributors map[string]Contributor
		Projects     map[string]Project
	}
)

func LoadProblem(in *bufio.Reader) (*Problem, error) {
	p := &Problem{
		Contributors: make(map[string]Contributor),
		Projects:     make(map[string]Project),
	}

	line, err := in.ReadString('\n')
	if err != nil {
		return p, fmt.Errorf("unable to read problem: %w", err)
	}

	C, P := split2ii(line)

	for i := 0; i < C; i++ {
		line, err := in.ReadString('\n')
		if err != nil {
			return p, fmt.Errorf("unable to read contributor #%d: %w", i+1, err)
		}

		contributorName, nskills := split2si(line)

		skills := make(map[string]Skill)

		for k := 0; k < nskills; k++ {
			line, err := in.ReadString('\n')
			if err != nil {
				return p, fmt.Errorf("unable to read skill #%d: %w", k+1, err)
			}

			skillName, level := split2si(line)

			skills[skillName] = Skill{
				Name:  skillName,
				Level: level,
			}
		}

		p.Contributors[contributorName] = Contributor{
			Name:   contributorName,
			Skills: skills,
		}
	}

	for i := 0; i < P; i++ {
		line, err := in.ReadString('\n')
		if err != nil {
			return p, fmt.Errorf("unable to read project #%d: %w", i+1, err)
		}

		prjName, duration, score, bestbefore, nroles := split2siiii(line)

		var roles []Skill

		for k := 0; k < nroles; k++ {
			line, err := in.ReadString('\n')
			if err != nil {
				return p, fmt.Errorf("unable to read role #%d: %w", k+1, err)
			}

			name, level := split2si(line)

			roles = append(roles, Skill{
				Name:  name,
				Level: level,
			})
		}

		p.Projects[prjName] = Project{
			Name:       prjName,
			Duration:   duration,
			Score:      score,
			BestBefore: bestbefore,
			Roles:      roles,
		}
	}

	return p, nil
}

func split(value string) []string {
	return strings.Split(strings.TrimSpace(value), " ")
}

func split2ss(value string) (string, string) {
	tokens := split(value)
	if len(tokens) != 2 {
		panic(value)
	}

	return tokens[0], tokens[1]
}

func split2ii(value string) (int, int) {
	t0, t1 := split2ss(value)

	r0, err := strconv.Atoi(t0)
	if err != nil {
		panic(value)
	}

	r1, err := strconv.Atoi(t1)
	if err != nil {
		panic(value)
	}

	return r0, r1
}

func split2si(value string) (string, int) {
	t0, t1 := split2ss(value)

	r1, err := strconv.Atoi(t1)
	if err != nil {
		panic(value)
	}

	return t0, r1
}

func split2siiii(value string) (string, int, int, int, int) {
	tokens := split(value)
	if len(tokens) != 5 {
		panic(value)
	}

	r1, err := strconv.Atoi(tokens[1])
	if err != nil {
		panic(value)
	}

	r2, err := strconv.Atoi(tokens[2])
	if err != nil {
		panic(value)
	}

	r3, err := strconv.Atoi(tokens[3])
	if err != nil {
		panic(value)
	}

	r4, err := strconv.Atoi(tokens[4])
	if err != nil {
		panic(value)
	}

	return tokens[0], r1, r2, r3, r4
}
