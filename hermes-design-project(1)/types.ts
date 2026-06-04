
export interface TeamMember {
  id: string;
  name: string;
  role: string;
  affiliation?: string;
  email: string;
  imageUrl?: string;
  initials: string;
}

export interface Deliverable {
  id: string;
  date: string;
  title: string;
  filename: string;
  downloadLink: string;
}

export interface Publication {
  id: string;
  date: string;
  title: string;
  authors: string;
  venue: string;
  link: string;
  artefactLink?: string;
  highlighted?: boolean;
}

export interface InvitedTalk {
  id: string;
  date: string;
  title: string;
  event: string;
  location?: string;
  link?: string;
}