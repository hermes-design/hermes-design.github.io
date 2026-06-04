export interface Author {
  name: string;
  link: string;
  isPresenter?: boolean;
  role?: string;
  university?: string;
  department?: string;
}

export interface Presentation {
  title: string;
  authors: Author[];
  slidesLink: string;
}

export interface ResourceLink {
  label: string;
  url: string;
}

export interface CodeResource {
  name: string;
  links: ResourceLink[];
}

export interface Tool {
  name: string;
  url: string;
  description: string;
}

export interface Project {
  name: string;
  url: string;
}

export interface SiteData {
  event: string;
  eventLink?: string;
  presentation: Presentation;
  sections: {
    codeResources: {
      title: string;
      items: CodeResource[];
    };
    caseStudies: {
      title: string;
      items: CodeResource[];
    };
    tools: {
      title: string;
      items: Tool[];
    };
    relatedProjects: {
      title: string;
      items: Project[];
    };
  };
}
