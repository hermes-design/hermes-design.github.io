
import { TeamMember, Deliverable, Publication, InvitedTalk } from './types';
import projectData from './data.json';

export const PROJECT_TITLE = projectData.projectInfo.title;
export const PROJECT_SUBTITLE = projectData.projectInfo.subtitle;
export const PROJECT_FUNDING = projectData.projectInfo.funding;

export const PROJECT_SUMMARY = projectData.projectInfo.summary;

export const TEAM_MEMBERS: TeamMember[] = projectData.teamMembers as TeamMember[];

export const DELIVERABLES: Deliverable[] = projectData.deliverables as Deliverable[];

export const PUBLICATIONS: Publication[] = projectData.publications as Publication[];

export const INVITED_TALKS: InvitedTalk[] = projectData.invitedTalks as InvitedTalk[];
