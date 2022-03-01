package main

type (
	Project struct {
		Name string

		Duration   int
		Score      int
		BestBefore int

		Roles []Skill
	}
)

func (p *Project) ScoreIfNow(startDay int) int {
	lateDays := startDay + p.Duration - p.BestBefore
	if lateDays > 0 {
		return p.Score - lateDays
	}

	return p.Score
}
