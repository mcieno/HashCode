package main

type (
	Contributor struct {
		Name   string
		Skills map[string]Skill
	}
)

func (c *Contributor) CanFill(role Skill, mentors []Contributor) bool {
	skill, ok := c.Skills[role.Name]
	if !ok {
		skill = Skill{
			Name:  role.Name,
			Level: 0,
		}
	}

	if skill.Level >= role.Level {
		return true
	}

	if role.Level-skill.Level > 1 {
		return false
	}

	for _, mentor := range mentors {
		mskill, ok := mentor.Skills[role.Name]
		if !ok {
			continue
		}

		if mskill.Level >= role.Level {
			return true
		}
	}

	return false
}

func (c *Contributor) Fill(role Skill) {
	skill, ok := c.Skills[role.Name]
	if !ok {
		skill = Skill{
			Name:  role.Name,
			Level: 0,
		}
	}

	if skill.Level <= role.Level {
		skill.Level++
	}

	if c.Skills == nil {
		c.Skills = make(map[string]Skill)
	}

	c.Skills[role.Name] = skill
}

func (c *Contributor) Unfill(role Skill) {
	skill, ok := c.Skills[role.Name]
	if !ok {
		return
	}

	if skill.Level > 0 {
		skill.Level--
	}

	c.Skills[role.Name] = skill
}
